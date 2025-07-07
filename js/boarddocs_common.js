// js/boarddocs_common.js

// Global mapping object for all dashboard pages
let mapping = {};

/**
 * Loads the mapping.json file for normalization functions.
 * Call `await loadMapping()` before using normalization!
 * @param {string} url - Path to mapping.json (default: "data/mapping.json")
 * @returns {Promise<void>}
 */
async function loadMapping(url = "data/mapping.json") {
  try {
    const resp = await fetch(url);
    mapping = await resp.json();
  } catch (e) {
    mapping = {};
    console.error("Could not load mapping.json:", e);
  }
}

/**
 * Normalize agenda item categories.
 * Always returns an array of category tags.
 * If not found in mapping, fallback is ["Other"].
 * @param {string} cat
 * @returns {string[]}
 */
function normalizeCategories(cat) {
  if (!cat) return ["Other"];
  // Prefer mapping file
  if (
    mapping.category &&
    typeof mapping.category[cat] === 'string' &&
    mapping.category[cat].trim() !== ""
  ) {
    return [mapping.category[cat]];
  }
  // --- Optional fallback: pattern/regex matching for legacy/unmapped cases ---
  // You can customize this or remove if all cases are mapped
  cat = cat.replace(/^\d+\.*\s*-*\s*/g, '').toLowerCase().trim();
  const regexFallback = [
    { tag: "Call to Order", regex: /call to order/ },
    { tag: "Pledge of Allegiance", regex: /pledge of allegiance/ },
    { tag: "Information", regex: /information|discussion|presentation|informational/ },
    { tag: "Recognition/Celebration", regex: /recognition|recognize|celebration|presentations? and celebrations?/ },
    { tag: "Call to the Public", regex: /call to the public|public comments?/ },
    { tag: "Approval of Minutes", regex: /approval of minutes|meeting minutes|minutes/ },
    { tag: "Action Items", regex: /action items?/ },
    { tag: "Consent Agenda Items", regex: /consent agenda/ },
    { tag: "Future Agenda Items", regex: /future agenda/ },
    { tag: "Return to Regular Session", regex: /return to regular session|reconvene|resturn to regular session|reconvene regular board meeting|reconvene meeting|reconvene the regular board meeting|reconvene to regular session/ },
    { tag: "Adjournment", regex: /adjourn(ment)?|adjourn excutive session|adjourn exutive session|adjourn excutiv(e)? session/ },
    { tag: "Executive Session", regex: /executive session|executive sesssion|excutive session|exective session/ },
    { tag: "Public Hearing", regex: /public hearing/ },
    { tag: "Recognitions", regex: /recognitions?/ },
    { tag: "Oath of Office/Election of Governing Board Officers", regex: /oath of office|election of governing board officers|nomination|nominations and election|election of governing board officers for/ },
    { tag: "Board Advisory Committee", regex: /advisory committee/ }
  ];
  const tags = [];
  for (let m of regexFallback) {
    if (cat.match(m.regex)) tags.push(m.tag);
  }
  if (tags.length === 0) tags.push("Other");
  return [...new Set(tags)];
}

/**
 * Normalize agenda item types.
 * Always returns an array of type tags (even for single/atomic types).
 * Compound types (like "Information, Presentation") become ["Information", "Presentation"].
 * If not found in mapping, fallback is empty array.
 * @param {string} type
 * @returns {string[]}
 */
function normalizeType(type) {
  if (!type) return [];
  // Prefer mapping file
  if (mapping.agenda_item_type && mapping.agenda_item_type[type]) {
    const arr = mapping.agenda_item_type[type];
    return Array.isArray(arr) ? arr.filter(Boolean) : [arr].filter(Boolean);
  }
  // --- Optional fallback: for legacy/unmapped types ---
  type = type.trim().toLowerCase();
  if (type === "procedural" || type === "procedure") return ["Procedural"];
  if (type === "action" || type === "action item" || type === "action items") return ["Action"];
  if (type === "informational" || type === "information") return ["Informational"];
  return [type.charAt(0).toUpperCase() + type.slice(1)];
}

/**
 * Normalize meeting types.
 * Always returns an array of meeting type tags (even for single/atomic meeting types).
 * If not found in mapping, fallback is empty array.
 * @param {string} meetingType
 * @returns {string[]}
 */
function normalizeMeetingType(meetingType) {
  if (!meetingType) return [];
  // Prefer mapping file
  if (mapping.meeting_type && mapping.meeting_type[meetingType]) {
    const arr = mapping.meeting_type[meetingType];
    return Array.isArray(arr) ? arr.filter(Boolean) : [arr].filter(Boolean);
  }
  // --- Optional fallback: for legacy/unmapped meeting types ---
  return [];
}

/**
 * Utility: Get unique sorted list from an array of arrays/values (for filters)
 * @param {Array} arrOfArrs
 * @returns {string[]} Sorted, unique, non-empty
 */
function getUniqueSorted(arrOfArrs) {
  return [...new Set(arrOfArrs.flat().filter(Boolean))].sort();
}

/**
 * Utility: Render array as comma-separated string, or fallback to "".
 * @param {string[]|string} val
 * @returns {string}
 */
function renderArray(val) {
  if (Array.isArray(val)) return val.join(", ");
  if (typeof val === "string") return val;
  return "";
}

/**
 * Utility: Checks if at least one element in arr matches any in filters.
 * Used for robust multi-tag filtering.
 * @param {string[]} arr
 * @param {string[]} filters
 * @returns {boolean}
 */
function anyTagMatch(arr, filters) {
  if (!filters.length) return true;
  if (!arr || !arr.length) return false;
  return arr.some(tag => filters.includes(tag));
}

/**
 * Utility: Deduplicate an array of objects by given keys.
 * @param {Array<Object>} arr - Array of objects to deduplicate.
 * @param {Array<string>} keys - Keys to use for uniqueness (e.g., ['name', 'vote']).
 * @returns {Array<Object>} Deduplicated array.
 */
function dedupeByKeys(arr, keys) {
  const seen = new Set();
  return arr.filter(item => {
    const key = keys.map(k => item[k]).join('|');
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}



// Add more utilities as your project grows!

// ---- End of boarddocs_common.js ----
