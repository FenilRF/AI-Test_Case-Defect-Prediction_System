/**
 * useSessionState — drop-in replacement for useState that persists to sessionStorage.
 *
 * Data survives sidebar navigation (component unmount/remount)
 * but is cleared when the tab is closed (sessionStorage spec).
 */

import { useState, useCallback } from "react";

/**
 * @param {string}  key           Unique sessionStorage key
 * @param {*}       defaultValue  Fallback when nothing is stored
 * @returns {[*, Function]}       Same API as useState
 */
export default function useSessionState(key, defaultValue) {
    const [value, setValue] = useState(() => {
        try {
            const stored = sessionStorage.getItem(key);
            return stored !== null ? JSON.parse(stored) : defaultValue;
        } catch {
            return defaultValue;
        }
    });

    const setSessionValue = useCallback(
        (newValue) => {
            setValue((prev) => {
                const resolved =
                    typeof newValue === "function" ? newValue(prev) : newValue;
                try {
                    sessionStorage.setItem(key, JSON.stringify(resolved));
                } catch {
                    /* storage full — degrade silently */
                }
                return resolved;
            });
        },
        [key]
    );

    return [value, setSessionValue];
}
