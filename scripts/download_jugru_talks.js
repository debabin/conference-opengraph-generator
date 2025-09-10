const downloadJugRuTalks = async () => {
  const talkCards = document.querySelectorAll(
    '[data-sentry-component="TalkCard"]'
  );

  const talks = [];

  talkCards.forEach((card) => {
    const titleElement = card.querySelector("h2, h3");
    const title = titleElement.textContent.trim();

    const descriptionElement = card.querySelector("p");
    const description = descriptionElement.textContent.trim();

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
      talk_description: description,
      avatar_url: avatar,
    });
  });

  const a = document.createElement("a");
  a.href = URL.createObjectURL(
    new Blob([JSON.stringify(talks, null, 2)], {
      type: "application/json",
    })
  );
  a.download = "jugru_talks.json";
  a.click();
};
downloadJugRuTalks();
