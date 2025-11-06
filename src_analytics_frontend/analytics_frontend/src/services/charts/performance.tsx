export const downsample = (arr: any[], maxPoints = 300) => {
  const step = Math.ceil(arr.length / maxPoints);
  return arr.filter((_, i) => i % step === 0);
};