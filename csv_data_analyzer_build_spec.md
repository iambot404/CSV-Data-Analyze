## Vercel Deployment (Important)

Design the application for Vercel serverless deployment from day one.

### Architecture
- Use Flask with a Vercel Python Function entry point (`api/index.py`).
- Configure routing using `vercel.json` if required.
- Keep request handlers stateless.
- Ensure the app works both locally and on Vercel.

### CSV Processing
- Process small CSV files in memory.
- Use `/tmp` only for temporary files.
- Never depend on persistent local storage.
- Set upload limits and reject oversized files gracefully.
- Clean temporary files after processing.
- Avoid background workers and long-running tasks.

### Libraries
- Pandas and NumPy for analysis.
- Matplotlib with the `Agg` backend.
- Keep dependencies lightweight.
- Check deployment compatibility and memory usage.

### Database
- Use Supabase for persistent analysis history and metadata.
- Do not store CSV files by default.
- Use Supabase Storage only if file persistence becomes necessary.
- Enforce user ownership and access control.

### Gemini API
- Store GEMINI_API_KEY in Vercel Environment Variables.
- Never expose API keys in frontend code.
- Implement request timeouts and API error handling.
- Send computed summaries instead of entire CSV datasets.

### Security
- Store all secrets in environment variables.
- Never commit `.env`.
- Add `.env.example`.
- Never expose Supabase service-role credentials to the browser.

### Deployment Testing
- Test the Vercel entry point.
- Verify CSV uploads, charts, Gemini responses, and Supabase operations.
- Test malformed and oversized files.
- Verify that the application does not depend on persistent filesystem access.

### Scalability
- Vercel is the primary deployment target for the MVP.
- Do not promise unlimited dataset sizes.
- If processing exceeds serverless execution or memory limits, move the analysis backend to Render or another container-based service while keeping the frontend on Vercel.


## Visual Design – Vector Art Direction

Create a premium AI SaaS dashboard using modern vector illustrations.

- Use original vector artwork generated with Gemini.
- Generate abstract geometric backgrounds, floating charts,
  CSV sheets, data streams, and AI-inspired illustrations.
- Use subtle blue, violet, and cyan gradients.
- Add soft glow effects and floating decorative elements.
- Use SVG illustrations where possible for scalability.
- Create custom illustrations for upload, empty, and loading states.
- Keep the dashboard clean, minimal, and professional.
- Use subtle animations without affecting performance.
- Ensure illustrations never obstruct data or controls.

Ask Gemini to generate the visual assets.
Do not use generic stock illustrations.
Do not use AI-generated fake charts or fake statistics.



## Also add login and signup 

## Perform testing of functionality
