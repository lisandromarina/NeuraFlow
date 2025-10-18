"use client";

import { useEffect } from "react";

export default function OAuthSuccessPage() {
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const provider = params.get("provider");

    // Send message to the opener window
    if (window.opener) {
      window.opener.postMessage(
        { success: true, provider, message: `${provider} connected!` },
        window.location.origin
      );
      window.close(); // close the popup
    }
  }, []);

  return (
    <div className="p-4">
      <h1>OAuth Successful!</h1>
      <p>You can close this window.</p>
    </div>
  );
}
