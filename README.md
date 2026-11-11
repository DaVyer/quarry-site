# Quarry site

Public pages for Quarry, served by GitHub Pages: the home page, the privacy policy
(English, French, Korean) and the closed beta presentation.

The app's code lives in a separate, private repository. The pages are generated from its
`strings.xml`, so the web policy always says what the app says:

```
python tools/build_site.py ../quarry .
```

Run it after changing the policy in the app, then commit and push.
