# Microsoft JSON schema publishing repository

This repository contains schemas which are published at  https://developer.microsoft.com/json-schemas/. Maintenance and publishing is performed by Microsoft employees from different organizations. 

**Important** You cannot access the schemas directly from above URL, they are simply hosted there based on the folder structure in this repository. Tools are pointing automatically to the exact schema files as needed.

Last updated: 27 May 2026

## Publishing Microsoft Json schemas to the centralized json schema repo

We launched a centralized GitHub repo for publishing Microsoft-owned json schemas. Previously, json schema files are published to a public site(http://json-schema.org) for universally hosting json-schema files and to other Microsoft sites such as dev.office.com. However, there is an inherent risk in using the public site and much benefit to customers to provide a single, supported location for all Microsoft json schemas.

Repo: https://github.com/Microsoft/json-schemas  
Admins: https://github.com/orgs/Microsoft/teams/json-schemas-admins
Public site: https://developer.microsoft.com/json-schemas
Owner: Vesa Juvonen vesaj@microsoft.com (Eastern European Time (EET))
Publishing: Self-publish via an admin from  your team. 
For publishing support or if you don't have an admin who can publish:
  - M365 Developer program engineering team: DevAppPortalEng@microsoft.com
  - Office Developer documentation team: opcontent@microsoft.com
  - Check the repo for someone in your org with Admin perms!
    
## Get started: Get admin perms

All Microsoft teams are welcome to publish schemas to this repo. Pick two team members and request admin perms. Submit your request to @Microsoft/json-schemas-admins for approval and cc: Vesa Juvonen. This may take some time, so please be sure to do this part in advance. 

After you're approved as an admin, you have the power to create your own folder, add your schemas, manage your pull requests, etc.


## Publish a new schema

1.     Create one folder per team in the repo. Consider keeping your folder structure as flat as reasonable. Each folder will become an element of the json URL (e.g. https://developer.microsoft.com/json-schemas/folder/schema_name.json) Use examples in the repo for guidance. Stay consistent.

2.     Create a working branch in GitHub and add your new schema file. Then open a PR to merge to the master branch. You'll need your other team member to approve, or you can ask any Admin. Changes should appear on the staging servers 2-15 minutes after merging to Main branch.

3.     After review, open a pull request and merge to Live branch. After approval, the new schema goes live in about 2-15 minutes.

### Troubleshooting

If your new schema doesn't appear, you'll need to "manually" publish it by copying it directly to the Azure storage repo. Find the team folder, drill down, and create a new version folder. Follow the example of previous schemas. Once you create the new version folder, copy your new schema. there. As of May 2026, the links to the Azure blob storage location for each folder is:

- api-extractor https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/api-extractor/
- copilot https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/copilot/
- core-build https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/core-build/
- dotnet https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/dotnet/
- fabric https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/fabric/
- heft https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/heft/
- lockfile-explorer https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/lockfile-explorer/
- office-js https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/office-js/
- pnp https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/pnp/
- rig-package https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/rig-package/
- rush https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/rush/
- sp https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/sp/
- spfx-build https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/spfx-build/
- spfx https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/spfx/
- teams-toolkit https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/teams-toolkit/
- teams https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/teams/
- tsdoc https://graphprodblobstorage.blob.core.windows.net/content/json-schemas/en-us/html/tsdoc/

**Important**  If you add a new root level folder then you need to send an email to devappportaleng@microsoft.com (developer app portal engineering team) and erquest they whitelist this folder for removing locale from the full URL. You do not need to do this for sub-folders. As mentioned, this is the team that hosts the Azure blob so reach out to them for support if needed. You'll find they're very responsive if you catch them on India time! 

## Update existing schemas

1. Create a branch in GitHub and make changes to existing schema files.
2. Open a PR and tag your other team admin as reviewers.
3. Once approved, merge your PR to **Main**.
4. After you verify your update was merged to **Main**, open a new PR and merge **Main** to **Live**. You may note other schema commits; up to you how to handle this but my theory is that if they're in **Main**, then they're ready to go live.
5. GOOD NEWS: For minor changes, i.e. schema changes that are just a few lines, you can skip creating your branch and make your changes in Main. This eliminates the churn. As admin, you OWN your own changes so be extra careful when doing this.

Generally, updates hit the front edge servers and replicate out fairly quickly like within 30 minutes but it can take up to 24 hours. To see your updated or new file, you may need to clear your cache.

Questions or issues? Email devappportaleng@microsoft.com (developer app portal engineering team). You can also consider opening an Issue, but it won't get action unless you tag someone.
