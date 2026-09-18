# Kira Live2D

Kira Core now has a Live2D runtime importer and OBS/browser renderer.

Open Kira Studio, choose the original Live2D ZIP and press **Install model**. The importer copies the model into ignored local runtime storage, normalizes filenames, rewrites model references, and fills the empty model groups from this specific Kira model:

- EyeBlink: ParamEyeLOpen
- LipSync: ParamMouthOpenY
- Head: ParamAngleX / ParamAngleY / ParamAngleZ
- Eyes: ParamEyeBallX / ParamEyeBallY
- Body: ParamBodyAngleX

The OBS overlay embeds the Live2D page transparently and reads the avatar state continuously.

The browser renderer needs Cubism Core. The current page loads Cubism Core and Pixi runtime in the browser. For a completely offline deployment, download the official Cubism SDK for Web after accepting Live2D's license and vendor the required runtime files locally. Do not redistribute Cubism Core without complying with Live2D's license.
