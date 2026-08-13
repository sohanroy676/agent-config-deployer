# Pre-Deploy Checklist

<!-- Run through this before deploying anywhere real users/traffic can reach. 
     Have Cline check each item against the actual code, don't just eyeball it. -->

## Security
- [ ] No secrets/API keys hardcoded anywhere in source (check `.env` is used, and is in `.gitignore`)
- [ ] No debug/test endpoints or admin backdoors left enabled
- [ ] Error messages shown to users don't leak stack traces, file paths, or internal details
- [ ] Dependencies have no known critical vulnerabilities (check Dependabot alerts)
- [ ] Input validation in place on anything user-facing (forms, API endpoints, file uploads)

## Correctness
- [ ] Full test suite passes
- [ ] CI is green on the latest commit
- [ ] Manually walked through the core user flow(s) end-to-end at least once

## Operational basics
- [ ] You know what the last-known-good commit/version is, and how to redeploy it if something breaks
- [ ] Basic error tracking is wired up if this is public-facing (e.g. Sentry free tier)
- [ ] `CHANGELOG.md` reflects what's actually shipping in this release

## Config
- [ ] Environment variables for production are set correctly (not pointing at dev/test values)
- [ ] Any "for testing only" flags, mock data, or seed data are removed or disabled
