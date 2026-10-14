const EVENT = "app-toast";

/** Fire a transient toast message (rendered by <Toaster /> in App). */
export function toast(message: string): void {
  window.dispatchEvent(new CustomEvent(EVENT, { detail: message }));
}

export function addToastListener(handler: (message: string) => void): () => void {
  const listener = (event: Event) => handler((event as CustomEvent<string>).detail);
  window.addEventListener(EVENT, listener);
  return () => window.removeEventListener(EVENT, listener);
}
