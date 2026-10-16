(() => {
  "use strict";

  const data = window.BIRDING_BINGO_DATA;
  const cardElement = document.getElementById("card");
  const statusElement = document.getElementById("status");
  const storageKey = "birding-bingo-montrose-v1";
  const freeIndex = 12;
  const lines = [];
  for (let row = 0; row < 5; row += 1) lines.push(Array.from({ length: 5 }, (_, col) => row * 5 + col));
  for (let col = 0; col < 5; col += 1) lines.push(Array.from({ length: 5 }, (_, row) => row * 5 + col));
  lines.push([0, 6, 12, 18, 24], [4, 8, 12, 16, 20]);

  if (!data || !Array.isArray(data.species) || data.species.length < 24) {
    statusElement.textContent = "Bird data is unavailable. Run the card generator to create birds.js.";
    return;
  }

  const weights = new Map(data.species);
  let state;

  function drawCard() {
    const available = data.species.map(([name, count]) => ({ name, count }));
    const card = [];
    for (let index = 0; index < 25; index += 1) {
      if (index === freeIndex) {
        card.push(null);
        continue;
      }
      const total = available.reduce((sum, bird) => sum + bird.count, 0);
      let choice = Math.random() * total;
      let picked = available.length - 1;
      for (let candidate = 0; candidate < available.length; candidate += 1) {
        choice -= available[candidate].count;
        if (choice < 0) {
          picked = candidate;
          break;
        }
      }
      card.push(available.splice(picked, 1)[0].name);
    }
    return card;
  }

  function validState(saved) {
    if (!saved || !Array.isArray(saved.card) || saved.card.length !== 25 ||
        saved.card[freeIndex] !== null || !Array.isArray(saved.marks)) return false;
    const names = saved.card.filter((name, index) => index !== freeIndex && typeof name === "string" && weights.has(name));
    return names.length === 24 && new Set(names).size === 24 &&
      saved.marks.every((index) => Number.isInteger(index) && index >= 0 && index < 25);
  }

  function save() {
    try { localStorage.setItem(storageKey, JSON.stringify(state)); } catch (_) { /* Browsers may disable storage. */ }
  }

  function render() {
    const marked = new Set(state.marks);
    marked.add(freeIndex);
    const completed = lines.filter((line) => line.every((index) => marked.has(index)));
    const bingoCells = new Set(completed.flat());
    cardElement.replaceChildren();

    state.card.forEach((name, index) => {
      const cell = document.createElement(index === freeIndex ? "div" : "button");
      cell.className = "cell";
      if (index === freeIndex) {
        cell.classList.add("free");
        cell.innerHTML = "FREE<br>SPACE";
      } else {
        cell.type = "button";
        cell.setAttribute("aria-pressed", String(marked.has(index)));
        const bird = document.createElement("strong");
        bird.textContent = name;
        const frequency = document.createElement("small");
        const percent = weights.get(name) / data.checklistCount * 100;
        frequency.textContent = `${percent < 10 ? percent.toFixed(1) : percent.toFixed(0)}% of lists`;
        cell.append(bird, frequency);
        cell.addEventListener("click", () => {
          if (marked.has(index)) state.marks = state.marks.filter((value) => value !== index);
          else state.marks.push(index);
          save();
          render();
          cardElement.children[index].focus();
        });
      }
      if (marked.has(index)) cell.classList.add("marked");
      if (bingoCells.has(index)) cell.classList.add("bingo");
      cardElement.append(cell);
    });

    const spotted = marked.size - 1;
    statusElement.textContent = completed.length
      ? `Bingo! ${completed.length} ${completed.length === 1 ? "line" : "lines"} complete · ${spotted} birds marked`
      : `${spotted} of 24 birds marked`;
  }

  try {
    const saved = JSON.parse(localStorage.getItem(storageKey));
    if (validState(saved)) state = saved;
  } catch (_) { /* Start a new card if storage is unavailable or damaged. */ }
  if (!state) state = { card: drawCard(), marks: [] };
  save();
  render();

  document.getElementById("reset").addEventListener("click", () => {
    state.marks = [];
    save();
    render();
  });
  document.getElementById("new-card").addEventListener("click", () => {
    const previous = state.card.join("|");
    const card = drawCard();
    if (card.join("|") === previous) [card[0], card[1]] = [card[1], card[0]];
    state = { card, marks: [] };
    save();
    render();
  });
})();
