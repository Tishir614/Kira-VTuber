# Exporting Kira for runtime

The uploaded/source Cubism project uses the .cmo3 authoring format. The runtime core cannot render that source file directly.

In Live2D Cubism Editor, export the model for runtime use. Keep the resulting .model3.json, .moc3, textures, physics, expressions and motion files together in one directory.

Put the exported directory under runtime/live2d/kira/ on the local machine. The runtime/ directory is intentionally ignored by Git so model assets are not accidentally published.

The next renderer layer will consume model3.json and map Kira Core states such as neutral, happy, sad, angry and surprised to expressions.
