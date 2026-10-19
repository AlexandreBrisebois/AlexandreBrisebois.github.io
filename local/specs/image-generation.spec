# Image Generation Specification (Multi-shot)

## Goal
Generate high-quality, brand-aligned hero images for blog posts using a multi-shot critique and refinement loop.

## Workflow
1.  **Extract Context**: Parse blog post frontmatter for `image_prompt`.
2.  **Prompt Review (Preflight)**:
    -   Review the `image_prompt` with a lower-cost text model before any image is generated.
    -   If the prompt does not match the brand or composition requirements, produce an updated prompt before Shot 1.
3.  **Model Discovery**: Identify the best available image generation model (Gemini-3-Pro-Image-Preview, Imagen-4, Imagen-3, etc.).
4.  **Initial Generation (Shot 1)**: Request an image from the API using the reviewed prompt.
5.  **Critique (Vision Loop)**:
    -   Provide the generated image and initial prompt to Gemini Pro Vision.
    -   Evaluate against brand aesthetic: "Calm Signal", minimalist, fine linework, textured gradients, and a restrained use of the srvrlss.dev palette.
    -   Check whether color usage feels intentional and distinct, with a warm off-white base and accents drawn from forest, coral, oceanic, plum, slate, gold, eucalyptus, sienna, mulberry, and bronze.
    -   Check for strict exclusions: No people, no faces, no logos.
6.  **Refine & Regenerate (Shot 2)**:
    -   If the critique is negative, refine the prompt with specific feedback.
    -   Regenerate the image.
7.  **Finalize**:
    -   Save the final image as WebP to `static/images/posts/<slug>.webp`.
    -   Update post frontmatter with `image: "/images/posts/<slug>.webp"`.

## Model Preferences
1. `gemini-3-pro-image-preview`
2. `imagen-4.0-generate-001`
3. `imagen-4.0-fast-generate-001`
4. `imagen-3.0-generate-002`
5. `imagen-3.0-generate-001`
6. `imagen-3.0-fast-generate-001`
7. `imagegeneration@006`

## Brand Aesthetic
- **Core**: Reflective-vulnerable, urgently excited.
- **Visuals**: Modern minimalist abstract, high-contrast textures.
- **Colors**: Warm off-white foundation with restrained accents from forest, coral, oceanic, plum, slate, gold, eucalyptus, sienna, mulberry, and bronze.
- **Style**: Linework, textured gradients, professional blog header style.
