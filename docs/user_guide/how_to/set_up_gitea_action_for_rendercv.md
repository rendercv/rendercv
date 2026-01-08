# Set Up Gitea Action for RenderCV

You can use workflows actions to run RenderCV on your repository containing your CV.

This allows you to automaticly render your CV when you push a change to your .yaml file.

This guide is written specificly for gitea, however it can apply to github / forgejo / etc... with a few tweaks. ( Namely changing varible names in the workflow.yaml )

## Prerequisites

1. You must have your RenderCV yaml file apart of it's own repository.
2. You must have an [act runner configured for gitea](https://docs.gitea.com/usage/actions/act-runner).
	- The specific configuration provided assumes your act runner is using the docker image.

## Creating the workflow

Create a file named rendercv.yml within .gitea/workflows

Example repository directory structure:
- RepoRoot/
    - .gitea/
        - workflows/
            - rendercv.yml
    - rendercv_output/
        - John_Doe_CV.png
        - John_Doe_CV.html
        - John_Doe_CV.pdf
        - John_Doe_CV.typ
        - John_Doe_CV.md
    - John_Doe_CV.yml
    - `README.md`
    
Add the following contents to: .gitea/workflows/rendercv.yml
```
name: RenderCV CI
on:
  push:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v6
      - name: Set up Python
        uses: actions/setup-python@v6
        cache: 'pip'
        with:
          python-version: '3.12'
      - name: Install RenderCV
        run: |
          pip install "rendercv[full]"
      - name: Run RenderCV
        run: |
          rendercv render "John_Doe_CV.yml"
      - name: Commit and Push changes
        run: |
          git config --global user.name "John Doe"
          git config --global user.email "JohnDoe@example.com"
          if git diff --quiet && git diff --staged --quiet; then
            echo "No changes to commit."
          else
            git commit -a -m "RenderCV for: ${{ gitea.event_name }}: ${{ gitea.sha }}"
            git push "https://${{ gitea.actor }}:${{ secrets.GITEA_TOKEN }}@gitea.example.com/${{ gitea.repository }}.git" HEAD:${{ gitea.ref_name }}
          fi
```
Edit the followings lines to account for your gitea user name, email, and URL:
`git config --global user.name "John Doe"` REPLACE: `John Doe`
`git config --global user.email "JohnDoe@example.com"` REPLACE: `JohnDoe@example.com`
`git push "https://${{ gitea.actor }}:${{ secrets.GITEA_TOKEN }}@gitea.example.com/${{ gitea.repository }}.git" HEAD:${{ gitea.ref_name }}` REPLACE: `gitea.example.com`
`runs-on: ubuntu-latest` This will need to match at least one label applied to your gitea act runner

## Checking your work

1. Push an edit to your CV.yml file.
2. Visit the Actions Tab of your repo to check the status of the workflow.
3. Click on the message of your commit to see step-by-step output from the action.

You will now have an automated CI for rendering your CV using RenderCV within your Gitea repo.

## Render to README

If you want, you can also tell RenderCV to change the file the markdown version points to:
```
settings:
  render_command:
    markdown_path: README.md
```
By changing it to just `README.md` now RenderCV will update the README for your repo with the latest version of your CV.
