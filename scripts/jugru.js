const talkCards = document.querySelectorAll(
  '[data-sentry-component="TalkCard"]'
);

const getLogo = async () => {
  const logoElement = document.querySelector('[data-sentry-component="Logo"]');
  const logoSrc = logoElement.src;

  const response = await fetch(logoSrc);
  const svgText = await response.text();

  return "data:image/svg+xml;base64," + btoa(svgText);
};

const talks = [];

talkCards.forEach((card) => {
  const titleElement = card.querySelector("h2, h3");
  const title = titleElement.textContent.trim();

  const speakerElement = card.querySelector("h3");
  const speaker = speakerElement.textContent.trim();

  const companyElement = card.querySelector(
    '[data-sentry-component="PersonCompany"]'
  );

  const company = companyElement?.textContent?.trim() ?? "";

  const imgElement = card.querySelector("img");
  let avatar = imgElement.src;

  if (avatar.includes("jugru.team")) {
    const url = new URL(avatar);
    url.searchParams.set("width", "350");
    url.searchParams.set("height", "350");
    url.searchParams.set("mode", "CropUpsize");
    avatar = url.href;
  }

  talks.push({
    name: speaker,
    job_title: company,
    talk_title: title,
    avatar_url: avatar,
  });
});

const a = document.createElement("a");
a.href = URL.createObjectURL(
  new Blob(
    [JSON.stringify({ speakers: talks, logo: await getLogo() }, null, 2)],
    {
      type: "application/json",
    }
  )
);
a.download = "jugru_talks.json";
a.click();
