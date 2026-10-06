const state = { date: new Date() };

const elements = {
  date: document.querySelector("#selected-date"),
  notice: document.querySelector("#notice"),
  list: document.querySelector("#trip-list"),
  form: document.querySelector("#trip-form"),
  net: document.querySelector("#net-total"),
  revenue: document.querySelector("#revenue-total"),
  commission: document.querySelector("#commission-total"),
  trips: document.querySelector("#trips-total"),
  badge: document.querySelector("#trips-badge"),
  cashTotal: document.querySelector("#cash-total"),
  cardTotal: document.querySelector("#card-total"),
  cashCount: document.querySelector("#cash-count"),
  cardCount: document.querySelector("#card-count"),
};

const money = (value) => `${new Intl.NumberFormat("ru-RU").format(value)} ₽`;
const dateKey = (date) => [date.getFullYear(), String(date.getMonth() + 1).padStart(2, "0"), String(date.getDate()).padStart(2, "0")].join("-");
const displayDate = (value) => new Intl.DateTimeFormat("ru-RU", { day: "2-digit", month: "long", year: "numeric" }).format(new Date(`${value}T12:00:00`));

function setNotice(message = "", isError = false) {
  elements.notice.textContent = message;
  elements.notice.classList.toggle("error", isError);
}

function offsetIso(localValue) {
  const localDate = new Date(localValue);
  const offset = -localDate.getTimezoneOffset();
  const sign = offset >= 0 ? "+" : "-";
  const hours = String(Math.floor(Math.abs(offset) / 60)).padStart(2, "0");
  const minutes = String(Math.abs(offset) % 60).padStart(2, "0");
  const localPart = localValue.length === 16 ? `${localValue}:00` : localValue;
  return `${localPart}${sign}${hours}:${minutes}`;
}

function formatTime(value) {
  return new Intl.DateTimeFormat("ru-RU", { hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

function renderSummary(summary) {
  elements.net.textContent = money(summary.net);
  elements.revenue.textContent = money(summary.revenue);
  elements.commission.textContent = money(summary.commission);
  elements.trips.textContent = summary.trips_count;
  elements.badge.textContent = `${summary.trips_count} ${summary.trips_count === 1 ? "запись" : "записей"}`;
  elements.cashTotal.textContent = money(summary.cash.revenue);
  elements.cardTotal.textContent = money(summary.card.revenue);
  elements.cashCount.textContent = `${summary.cash.trips_count} поездок`;
  elements.cardCount.textContent = `${summary.card.trips_count} поездок`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#039;", '"': "&quot;" })[character]);
}

function renderTrips(trips) {
  if (!trips.length) {
    elements.list.innerHTML = '<div class="empty-state">За этот день поездок нет.<br>Добавьте первую запись справа.</div>';
    return;
  }
  elements.list.innerHTML = trips.map((trip, index) => `
    <article class="trip-row" style="animation-delay: ${index * 45}ms">
      <time class="trip-time">${formatTime(trip.start)}</time>
      <div><div class="trip-id">${escapeHtml(trip.id)}</div><div class="trip-route">до ${formatTime(trip.end)} · комиссия ${money(trip.commission)}</div></div>
      <span class="trip-payment">${trip.payment === "cash" ? "наличные" : "карта"}</span>
      <strong class="trip-amount">${money(trip.amount)}</strong>
    </article>`).join("");
}

async function loadDay() {
  const selectedDate = elements.date.value;
  document.querySelector("#day-label").textContent = displayDate(selectedDate);
  elements.list.innerHTML = '<div class="loading-state">Загрузка журнала<span class="loading-dots">...</span></div>';
  setNotice();
  try {
    const [summaryResponse, tripsResponse] = await Promise.all([
      fetch(`/api/summary?date=${selectedDate}`),
      fetch(`/api/trips?date=${selectedDate}`),
    ]);
    if (!summaryResponse.ok || !tripsResponse.ok) throw new Error("Сервер не смог загрузить данные");
    renderSummary(await summaryResponse.json());
    renderTrips(await tripsResponse.json());
  } catch (error) {
    elements.list.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}<br>Проверьте, запущен ли сервер.</div>`;
    setNotice(error.message, true);
  }
}

function shiftDay(amount) {
  state.date.setDate(state.date.getDate() + amount);
  elements.date.value = dateKey(state.date);
  loadDay();
}

elements.date.value = dateKey(state.date);
document.querySelector("#previous-day").addEventListener("click", () => shiftDay(-1));
document.querySelector("#next-day").addEventListener("click", () => shiftDay(1));
elements.date.addEventListener("change", () => {
  state.date = new Date(`${elements.date.value}T12:00:00`);
  loadDay();
});

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(elements.form);
  const payload = {
    id: formData.get("id"),
    start: offsetIso(formData.get("start")),
    end: offsetIso(formData.get("end")),
    amount: Number(formData.get("amount")),
    payment: formData.get("payment"),
    commission: Number(formData.get("commission")),
  };
  try {
    const response = await fetch("/api/trips", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const body = await response.json();
    if (!response.ok) throw new Error(body.detail?.map((error) => error.msg).join(", ") || "Не удалось сохранить поездку");
    setNotice(body.message);
    if (response.status === 201) elements.form.reset();
    await loadDay();
  } catch (error) {
    setNotice(error.message, true);
  }
});

loadDay();
