# Publishing AutoSleeper v1.0.0

The existing GitHub Actions workflow automatically builds on tag pushes and prepares a **draft** release. It does **not** publish automatically.

## Step 1 — Install documentation

Copy `README.md`, `RELEASE_NOTES_v1.0.0.md`, and `RELEASE_CHECKLIST_v1.0.md` into your AutoSleeper project root. Review the existing README before replacing it.

If you wish to license the source as open source, select and add a `LICENSE` file first; do not add a license without choosing its terms.

## Step 2 — Commit before tagging

```powershell
git switch main
git pull --ff-only origin main
git status
git add README.md RELEASE_NOTES_v1.0.0.md RELEASE_CHECKLIST_v1.0.md
git commit -m "Prepare AutoSleeper v1.0 stable release"
git push origin main
```

If there are no changes to commit, continue without creating an empty commit.

## Step 3 — Validate

Complete all items in `RELEASE_CHECKLIST_v1.0.md`. In particular, download and run the current Windows artifact built by GitHub Actions and ensure the shutdown behavior is safe. Do not tag the release before validation.

## Step 4 — Tag the exact validated commit

```powershell
git status
git tag -a v1.0.0 -m "AutoSleeper v1.0.0 stable"
git push origin v1.0.0
```

Ensure `git status` is clean and you are on the validated commit. If the tag already exists, stop and inspect it; do not force-push or overwrite a release tag.

## Step 5 — Review and publish the GitHub draft

1. Open the new GitHub Actions run triggered by `v1.0.0`.
2. Confirm both jobs succeed.
3. Open GitHub **Releases** and edit the automatically created `v1.0.0` draft.
4. Paste `RELEASE_NOTES_v1.0.0.md` into the description, replacing generic auto-generated notes if desired.
5. Check `AutoSleeper.exe` and `AutoSleeper.exe.sha256` under **Assets**.
6. Make sure the release is **not** labelled *Pre-release*.
7. Confirm the checksum and publish.

If the repository is private, only people with repository access can use the release. Change visibility only if you intentionally want public access to the source and release assets.
