export function formatISK(amount: number): string {
  if (amount >= 1000000000) {
    return `${(amount / 1000000000).toFixed(2)}B ISK`;
  }
  if (amount >= 1000000) {
    return `${(amount / 1000000).toFixed(2)}M ISK`;
  }
  if (amount >= 1000) {
    return `${(amount / 1000).toFixed(1)}K ISK`;
  }
  return `${amount.toFixed(0)} ISK`;
}

export function formatVolume(volume: number): string {
  if (volume >= 1000000) {
    return `${(volume / 1000000).toFixed(2)}M m³`;
  }
  if (volume >= 1000) {
    return `${(volume / 1000).toFixed(1)}K m³`;
  }
  return `${volume.toFixed(0)} m³`;
}

export function formatTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours >= 24) {
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return `${days}d ${remainingHours}h ${minutes}m`;
  }
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  
  if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  }
  
  return `${secs}s`;
}

export function calculateMargin(cost: number, revenue: number): number {
  if (cost === 0) return 0;
  return ((revenue - cost) / cost) * 100;
}

export function applyDiscount(price: number, discountPercent: number): number {
  return price * (1 - discountPercent / 100);
}

export function getDiscountForLocation(location: string): number {
  const discounts: Record<string, number> = {
    'RD-G2R': 5,
    'VA6-ED': 8,
    'D-PN': 10,
    'O-BKJY': 10,
    '7-60QB': 10,
    'PJ-LON': 12,
    'Z-7O': 12,
    'N-8YET': 10,
    'M-OEE8': 10,
  };
  return discounts[location] || 0;
}

export function isWinterCoSystem(system: string): boolean {
  const winterCoSystems = [
    'D-PN', 'VA6-ED', 'RD-G2R', 'O-BKJY', '7-60QB', 'X-7OMU',
    'E-YCML', 'H-PA29', 'F-9CZX', 'FDZ4-A', 'B-VIP9', 'V7-MID',
    'PJ-LON', 'Z-7O', 'N-8YET', 'M-OEE8'
  ];
  return winterCoSystems.includes(system.toUpperCase());
}
