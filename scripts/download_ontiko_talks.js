const downloadOntikoTalks = async () => {
  const talkCards = document.querySelectorAll(".thesis__item");

  const talks = [];

  talkCards.forEach((talkElement) => {
    const titleElement = talkElement.querySelector("h2");
    const title = titleElement.textContent.trim();

    const descriptionElement = talkElement.querySelector(".thesis__text");
    const description = descriptionElement.textContent.trim();

    const speakerElement = talkElement.querySelector(".thesis__author-name");
    const speaker = speakerElement.textContent.trim();

    const companyElement = talkElement.querySelector(".thesis__author-company");
    const company = companyElement.textContent.trim();

    const avatarElement = talkElement.querySelector(".thesis__author-img");
    const avatarStyle = window.getComputedStyle(avatarElement);
    const backgroundImage = avatarStyle.backgroundImage;
    const avatar = backgroundImage.slice(5, -2);

    talks.push({
      name: speaker,
      job_title: company,
      talk_title: title,
      talk_description: description,
      avatar_url: avatar,
    });
  });

  console.log(`Найдено ${talks.length} докладов`);
  console.log(JSON.stringify(talks, null, 2));

  const a = document.createElement("a");
  a.href = URL.createObjectURL(
    new Blob([JSON.stringify(talks, null, 2)], {
      type: "application/json",
    })
  );
  a.download = "ontiko_talks.json";
  a.click();
};

downloadOntikoTalks();
