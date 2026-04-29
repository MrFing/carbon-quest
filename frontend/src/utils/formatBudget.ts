export function formatBudget(amount: number): string {
  return `$${amount.toLocaleString("en-US")}`;
}

export function getBudgetColor(amount: number): string {
  if (amount < 5_000) {
    return "#ef4444";
  }
  if (amount <= 15_000) {
    return "#fbbf24";
  }
  return "#22c55e";
}
