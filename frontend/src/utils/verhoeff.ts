// Statutory Verhoeff D5 Checksum Implementation (UIDAI Aadhaar Standard)

const VERHOEFF_D: number[][] = [
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
  [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
  [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
  [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
  [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
  [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
  [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
  [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
  [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
  [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
];

const VERHOEFF_P: number[][] = [
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
  [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
  [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
  [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
  [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
  [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
  [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
  [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
];

export function validateVerhoeff(numStr: string): boolean {
  const clean = numStr.replace(/\D/g, "");
  if (clean.length !== 12) return false;
  let c = 0;
  const reversed = clean.split("").reverse();
  for (let i = 0; i < reversed.length; i++) {
    const digit = parseInt(reversed[i], 10);
    c = VERHOEFF_D[c][VERHOEFF_P[i % 8][digit]];
  }
  return c === 0;
}

export function redactAadhaarInPlace(numStr: string): string {
  const clean = numStr.replace(/\D/g, "");
  if (clean.length === 12) {
    return `[Aadhaar Redacted-••••-••••-${clean.slice(8)}]`;
  }
  return `[Aadhaar In-Memory Masked]`;
}

const STATE_CODE_MAP: Record<string, string> = {
  "01": "Jammu & Kashmir",
  "02": "Himachal Pradesh",
  "03": "Punjab",
  "04": "Chandigarh",
  "06": "Haryana",
  "07": "Delhi",
  "08": "Rajasthan",
  "09": "Uttar Pradesh",
  "10": "Bihar",
  "19": "West Bengal",
  "21": "Odisha",
  "22": "Chhattisgarh",
  "23": "Madhya Pradesh",
  "24": "Gujarat",
  "27": "Maharashtra",
  "29": "Karnataka",
  "32": "Kerala",
  "33": "Tamil Nadu",
  "36": "Telangana",
  "37": "Andhra Pradesh",
};

const ENTITY_TYPE_MAP: Record<string, string> = {
  P: "Individual / Sole Proprietorship",
  C: "Private Limited Company",
  F: "Partnership Firm / LLP",
  H: "Hindu Undivided Family (HUF)",
  A: "Association of Persons (AOP)",
  T: "Trust",
  X: "Synthetic Benchmark Entity",
};

export function decodeGSTIN(rawGstin: string): {
  stateName: string;
  entityType: string;
  isValidFormat: boolean;
} | null {
  const clean = rawGstin.trim().toUpperCase();
  if (clean.length < 2) return null;

  const stateCode = clean.slice(0, 2);
  const stateName = STATE_CODE_MAP[stateCode] || `State Code ${stateCode}`;

  let entityType = "Unknown Entity";
  if (clean.length >= 6) {
    const entityChar = clean.charAt(5); // 4th character of embedded PAN (index 5 of GSTIN)
    entityType = ENTITY_TYPE_MAP[entityChar] || `Type Code ${entityChar}`;
  }

  // GSTIN regex accepting 'X' benchmark anomaly
  const gstinRegex = /^[0-9]{2}[A-Z]{3}[ABCFGHLJPTFX][A-Z][0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/;
  const isValidFormat = gstinRegex.test(clean);

  return { stateName, entityType, isValidFormat };
}
