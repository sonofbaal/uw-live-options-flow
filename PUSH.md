# How to push this to your GitHub

This folder is already a git repo with an initial commit. You just need to create
the repo on GitHub and push. Replace `YOUR_USERNAME` with your GitHub username.

## Option A — with the GitHub CLI (`gh`)

Easiest if you have `gh` installed and logged in (`gh auth status` to check):

```bash
cd uw-live-options-flow
gh repo create uw-live-options-flow --public --source=. --remote=origin --push
```

That creates the repo and pushes in one step.

## Option B — plain git

1. On github.com, click **New repository**, name it `uw-live-options-flow`, set it
   **Public**, and do NOT add a README/license (this folder already has them). Create.

2. Back in the terminal:

```bash
cd uw-live-options-flow
git remote add origin https://github.com/YOUR_USERNAME/uw-live-options-flow.git
git branch -M main
git push -u origin main
```

## Turn on the live demo (GitHub Pages)

1. In the repo on GitHub: **Settings → Pages**.
2. Under **Source**, pick **Deploy from a branch**.
3. Branch: **main**, folder: **/ (root)**. Save.
4. Wait ~1 minute. Your live dashboard is at:
   `https://YOUR_USERNAME.github.io/uw-live-options-flow/`

Then edit the **Live demo** line at the top of `README.md` to that URL, commit, and push:

```bash
git commit -am "Add live demo link"
git push
```

## After it's up

- The repo link and the Pages link are both good to drop in the Discord post.
- To refresh the live demo with newer data later: run `python3 build_dashboard.py`,
  copy the new `uw_flow_dashboard.html` over `index.html`, commit, and push.
