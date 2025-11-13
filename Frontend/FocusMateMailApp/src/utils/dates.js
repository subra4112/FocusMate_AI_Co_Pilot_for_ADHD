const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export function formatRelativeTimestamp(dateString) {
  if (!dateString) {
    return "";
  }
  const date = new Date(dateString);
  const now = new Date();
  const sameDay = date.toDateString() === now.toDateString();
  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  const isYesterday = date.toDateString() === yesterday.toDateString();

  const hours = date.getHours();
  const minutes = date.getMinutes().toString().padStart(2, "0");
  const suffix = hours >= 12 ? "PM" : "AM";
  const hour12 = hours % 12 || 12;
  const time = `${hour12}:${minutes} ${suffix}`;

  if (sameDay) {
    return `Today • ${time}`;
  }
  if (isYesterday) {
    return `Yesterday • ${time}`;
  }

  return `${DAYS[date.getDay()]} • ${time}`;
}

export function formatDueLabel(dueString) {
  if (!dueString) {
    return null;
  }
  const dueDate = new Date(dueString);
  const now = new Date();
  const diff = dueDate.getTime() - now.getTime();
  const diffDays = Math.ceil(diff / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return "Past due";
  }
  if (diffDays === 0) {
    return "Due today";
  }
  if (diffDays === 1) {
    return "Due tomorrow";
  }
  return `Due in ${diffDays} days`;
}

