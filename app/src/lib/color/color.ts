export interface Color {
  r: number;
  g: number;
  b: number;
}
export function colerp(start: Color, end: Color, value: number) {
  const r = Math.round(start.r + (end.r - start.r) * value);
  const g = Math.round(start.g + (end.g - start.g) * value);
  const b = Math.round(start.b + (end.b - start.b) * value);

  return `rgb(${r}, ${g}, ${b})`;
}
