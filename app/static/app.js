const state = { date: new Date(), page: 1, pageSize: 10, trips: [] };

const elements = {
  date: document.querySelector("#selected-date"),
  dateCaption: document.querySelector("#date-caption"),
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
  addModal: document.querySelector("#add-modal"),
  formError: document.querySelector("#form-error"),
  formErrorMessage: document.querySelector("#form-error-message"),
  tripModal: document.querySelector("#trip-modal"),
  tripDetailTitle: document.querySelector("#trip-detail-title"),
  tripDetailContent: document.querySelector("#trip-detail-content"),
  pageInfo: document.querySelector("#page-info"),
  previousPage: document.querySelector("#previous-page"),
  nextPage: document.querySelector("#next-page"),
};

const money = (value) => `${new Intl.NumberFormat("ru-RU").format(value)} ₽`;
const dateKey = (date) => [date.getFullYear(), String(date.getMonth() + 1).padStart(2, "0"), String(date.getDate()).padStart(2, "0")].join("-");
const displayDate = (value) => new Intl.DateTimeFormat("ru-RU", { day: "2-digit", month: "long", year: "numeric" }).format(new Date(`${value}T12:00:00`));

function setNotice(message = "", isError = false) {
  elements.notice.textContent = message;
  elements.notice.classList.toggle("error", isError);
}

function setFormError(message = "") {
  elements.formErrorMessage.textContent = message;
  elements.formError.hidden = !message;
}

function getApiErrorMessage(body) {
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail)) {
    return body.detail.map((error) => error.msg.replace(/^Value error,\s*/i, "")).join("; ");
  }
  return "Не удалось сохранить поездку";
}

function prepareTripForm() {
  const form = elements.form;
  form.elements["start-date"].value = elements.date.value;
  form.elements["start-time"].value = "12:00";
  form.elements["end-date"].value = elements.date.value;
  form.elements["end-time"].value = "12:30";
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

function renderPagination(pageData) {
  const firstItem = pageData.total ? (pageData.page - 1) * pageData.page_size + 1 : 0;
  const lastItem = Math.min(pageData.page * pageData.page_size, pageData.total);
  elements.pageInfo.textContent = pageData.total
    ? `${firstItem}–${lastItem} из ${pageData.total} · стр. ${pageData.page}/${pageData.total_pages}`
    : "Нет поездок";
  elements.previousPage.disabled = pageData.page <= 1;
  elements.nextPage.disabled = pageData.page >= pageData.total_pages;
}

function renderTrips(pageData) {
  state.trips = pageData.items;
  renderPagination(pageData);
  if (!pageData.items.length) {
    elements.list.innerHTML = '<div class="empty-state">За этот день поездок нет.<br>Добавьте первую запись во вкладке «Добавить поездку».</div>';
    return;
  }
  elements.list.innerHTML = pageData.items.map((trip, index) => `
    <button class="trip-row" data-trip-index="${index}" type="button" style="animation-delay: ${index * 45}ms">
      <time class="trip-time">${formatTime(trip.start)}</time>
      <span><span class="trip-id">${escapeHtml(trip.id)}</span><span class="trip-route">до ${formatTime(trip.end)} · нажмите для деталей</span></span>
      <span class="trip-payment">${trip.payment === "cash" ? "наличные" : "карта"}</span>
      <span class="trip-figures"><strong>${money(trip.amount - trip.commission)}</strong><small>на руки</small></span>
    </button>`).join("");
}

function formatDuration(start, end) {
  const minutes = Math.max(0, Math.round((new Date(end) - new Date(start)) / 60000));
  return `${Math.floor(minutes / 60)} ч ${String(minutes % 60).padStart(2, "0")} мин`;
}

function renderTripDetails(trip) {
  elements.tripDetailTitle.textContent = trip.id;
  elements.tripDetailContent.innerHTML = `
    <div class="detail-meta"><span>${trip.payment === "cash" ? "Наличные" : "Карта"}</span><span>${formatDuration(trip.start, trip.end)}</span></div>
    <div class="detail-times"><div><small>Начало</small><strong>${formatTime(trip.start)}</strong></div><span>→</span><div><small>Окончание</small><strong>${formatTime(trip.end)}</strong></div></div>
    <div class="detail-money">
      <div><small>Выручка</small><strong>${money(trip.amount)}</strong></div>
      <div><small>Комиссия</small><strong class="detail-money--commission">− ${money(trip.commission)}</strong></div>
      <div class="detail-money--net"><small>На руки</small><strong>${money(trip.amount - trip.commission)}</strong></div>
    </div>`;
}

function setTripModalState(isOpen) {
  elements.tripModal.classList.toggle("is-open", isOpen);
  elements.tripModal.setAttribute("aria-hidden", String(!isOpen));
  document.body.classList.toggle("modal-open", isOpen || elements.addModal.classList.contains("is-open"));
}

async function loadDay(resetPage = false) {
  if (resetPage) state.page = 1;
  const selectedDate = elements.date.value;
  const formattedDate = displayDate(selectedDate);
  elements.dateCaption.textContent = formattedDate;
  document.querySelector("#day-label").textContent = formattedDate;
  elements.list.innerHTML = '<div class="loading-state">Загрузка журнала<span class="loading-dots">...</span></div>';
  setNotice();
  try {
    const [summaryResponse, tripsResponse] = await Promise.all([
      fetch(`/api/summary?date=${selectedDate}`),
      fetch(`/api/trips?date=${selectedDate}&page=${state.page}&page_size=${state.pageSize}`),
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
  loadDay(true);
}

elements.date.value = dateKey(state.date);
elements.dateCaption.textContent = displayDate(elements.date.value);
document.querySelector("#previous-day").addEventListener("click", () => shiftDay(-1));
document.querySelector("#next-day").addEventListener("click", () => shiftDay(1));
elements.date.addEventListener("change", () => {
  state.date = new Date(`${elements.date.value}T12:00:00`);
  loadDay(true);
});

elements.previousPage.addEventListener("click", () => {
  if (state.page > 1) {
    state.page -= 1;
    loadDay();
  }
});
elements.nextPage.addEventListener("click", () => {
  state.page += 1;
  loadDay();
});

elements.list.addEventListener("click", (event) => {
  const row = event.target.closest("[data-trip-index]");
  if (!row) return;
  renderTripDetails(state.trips[Number(row.dataset.tripIndex)]);
  setTripModalState(true);
});

document.querySelector("#close-trip-modal").addEventListener("click", () => setTripModalState(false));
elements.tripModal.addEventListener("click", (event) => {
  if (event.target === elements.tripModal) setTripModalState(false);
});

function setModalState(isOpen) {
  elements.addModal.classList.toggle("is-open", isOpen);
  elements.addModal.setAttribute("aria-hidden", String(!isOpen));
  document.body.classList.toggle("modal-open", isOpen || elements.tripModal.classList.contains("is-open"));
  if (isOpen) {
    prepareTripForm();
    setFormError();
  }
}

document.querySelector("#open-add-modal").addEventListener("click", () => setModalState(true));
document.querySelector("#close-add-modal").addEventListener("click", () => {
  setFormError();
  setModalState(false);
});
document.querySelector("#close-form-error").addEventListener("click", () => setFormError());
elements.addModal.addEventListener("click", (event) => {
  if (event.target === elements.addModal) setModalState(false);
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && elements.addModal.classList.contains("is-open")) setModalState(false);
  if (event.key === "Escape" && elements.tripModal.classList.contains("is-open")) setTripModalState(false);
});

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setFormError();
  const formData = new FormData(elements.form);
  const startLocal = `${formData.get("start-date")}T${formData.get("start-time")}`;
  const endLocal = `${formData.get("end-date")}T${formData.get("end-time")}`;
  const payload = {
    id: formData.get("id"),
    start: offsetIso(startLocal),
    end: offsetIso(endLocal),
    amount: Number(formData.get("amount")),
    payment: formData.get("payment"),
    commission: Number(formData.get("commission")),
  };
  try {
    const response = await fetch("/api/trips", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const body = await response.json();
    if (!response.ok) throw new Error(getApiErrorMessage(body));
    setNotice(body.message);
    if (response.status === 201) elements.form.reset();
    await loadDay(true);
    setModalState(false);
  } catch (error) {
    setFormError(error.message);
  }
});

loadDay();
