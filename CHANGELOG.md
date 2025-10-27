# CHANGELOG

<!-- version list -->

## v0.1.0 (2025-10-23)

### Documentation

- **readme**: Add note on c2pie version
  ([`3726a77`](https://github.com/TourmalineCore/c2pie/commit/3726a77c113c4dff2b344897af5f8b68521994dd))

- **readme**: Change latest version reference
  ([`6409e05`](https://github.com/TourmalineCore/c2pie/commit/6409e05957922b98883326c6d8c78af0f8b1346e))

- **readme**: Remove note of package version in descr, change badge label
  ([`a6efaf9`](https://github.com/TourmalineCore/c2pie/commit/a6efaf9f35ce21db4b041d97fd3fca8ad6d8445b))

### Features

- Implement JPEG and PDF C2PA signing functionality
  ([`5f6b761`](https://github.com/TourmalineCore/c2pie/commit/5f6b76145d99c399a1db48de37fb86d47d0f3e26))

- **example-app**: Add ability to set c2pie version that should be used in example app
  ([`c9c95eb`](https://github.com/TourmalineCore/c2pie/commit/c9c95eb4c50f756735d9c0c71ea65d673363da04))


## v0.1.0-alpha.6 (2025-10-17)

### Bug Fixes

- **example-app**: Switch to installing c2pie as a pypi package
  ([`aff1f38`](https://github.com/TourmalineCore/c2pie/commit/aff1f38e93549ca09ae9529af529c1d2eb5c27a6))

### Documentation

- **readme**: Add latest version mentioning
  ([`d78cd45`](https://github.com/TourmalineCore/c2pie/commit/d78cd45d77379e951dea7465e8c2bf5ea8ca1430))

### Features

- **semantic-release**: Try to exclude semantic-release commits from changelog
  ([`ebf5a54`](https://github.com/TourmalineCore/c2pie/commit/ebf5a549ee63480af4f619edaa88fefa088ad308))

- **semantic-release**: Try to exclude workflows commits from changelog
  ([`7f196fb`](https://github.com/TourmalineCore/c2pie/commit/7f196fb51654c7115ca0260ffa791d6e675c5b75))


## v0.1.0-alpha.5 (2025-10-16)

### Bug Fixes

- **semantic-releases**: Fix workflows not being ignored in changelog
  ([`65c7432`](https://github.com/TourmalineCore/c2pie/commit/65c7432e4762074302c108f125cd2eb3c65276c3))

- **workflows**: Fix workflows still triggering on push at the same time as release
  ([`9469203`](https://github.com/TourmalineCore/c2pie/commit/94692034e1a8c164ce53256a0d23c70ce3a4c227))


## v0.1.0-alpha.4 (2025-10-16)

### Bug Fixes

- **readme**: Fix not working links to banner
  ([`96217d6`](https://github.com/TourmalineCore/c2pie/commit/96217d60dfcab0dd8f59156763766b0334c47a7f))

- **semantic-release**: Ignore test coverage badge updates in changelog
  ([`be590a2`](https://github.com/TourmalineCore/c2pie/commit/be590a28dfe8c895609aa582eb3179a66199f5df))

- **semantic-release**: Not trigger workflows on push by semantic-release
  ([`239b3c5`](https://github.com/TourmalineCore/c2pie/commit/239b3c5e83857c629ea74fb15b1604fc11073880))

- **workflows**: Add debug
  ([`6c28056`](https://github.com/TourmalineCore/c2pie/commit/6c280564995d0794d321cd44a3c650e7ddd6d918))

- **workflows**: Add debuging and fix option for grep
  ([`2b3c9ef`](https://github.com/TourmalineCore/c2pie/commit/2b3c9efd799329f63c7744a4f91a12bacac8e80f))

- **workflows**: Add processing url non-existence
  ([`01a544f`](https://github.com/TourmalineCore/c2pie/commit/01a544faad87e0cdb13274f9e9d1f48e12585e38))

- **workflows**: Add sudo in download jq step
  ([`fc01ea3`](https://github.com/TourmalineCore/c2pie/commit/fc01ea3b7c4309ce3efeaa519d6140a0e6a26ae4))

- **workflows**: Bring back env vars names
  ([`15d0349`](https://github.com/TourmalineCore/c2pie/commit/15d0349ce0a6866e6a321527df084693478c5994))

- **workflows**: Bring back exporting vars
  ([`55b5418`](https://github.com/TourmalineCore/c2pie/commit/55b5418371b84abb59a06bc2191b4c3694c3841e))

- **workflows**: Change way of accessing environment variables
  ([`5b4e501`](https://github.com/TourmalineCore/c2pie/commit/5b4e5015dce34e2846232bc67f1efb52f7dad124))

- **workflows**: Convert str to int
  ([`69b1f73`](https://github.com/TourmalineCore/c2pie/commit/69b1f73948395951e7e6b54842ac2aafd1aa7ea7))

- **workflows**: Correct syntax according to github actions rules
  ([`041d51b`](https://github.com/TourmalineCore/c2pie/commit/041d51bef3f514c5bc061e382f5ac19ba5b9acd4))

- **workflows**: Export variables to github_env
  ([`ee93cfd`](https://github.com/TourmalineCore/c2pie/commit/ee93cfd7dd302a59765ca94c368eb2e1bf7bf689))

- **workflows**: Fix combined coverage treated as dir
  ([`6dc092a`](https://github.com/TourmalineCore/c2pie/commit/6dc092a257604e2ce0812adbb88785124876ef27))

- **workflows**: Fix finding current color
  ([`7a28fe8`](https://github.com/TourmalineCore/c2pie/commit/7a28fe80e5504bd4100a33b37fe2cf8c1c8e69f5))

- **workflows**: Fix string replacement
  ([`72bcdae`](https://github.com/TourmalineCore/c2pie/commit/72bcdaea479d1c9151c6d35a05f21ed7227cd529))

- **workflows**: Fix workflow permissions
  ([`cf7fb7b`](https://github.com/TourmalineCore/c2pie/commit/cf7fb7b24d86316dbfa6b76405bb41b0743a0813))

- **workflows**: Fix workflows still triggering on push at the same time as release
  ([`6e4f656`](https://github.com/TourmalineCore/c2pie/commit/6e4f656282544d8761b99a9e449f5e59c0019bf6))

- **workflows**: Remove escaping, add quotes to github env
  ([`46a920a`](https://github.com/TourmalineCore/c2pie/commit/46a920a9f1328edc385e37e9ec1fb9551b20206e))

- **workflows**: Try replacing score with a python script
  ([`5d3bb32`](https://github.com/TourmalineCore/c2pie/commit/5d3bb3208486451d2ca3c39893ebb9e503f4ccae))

- **workflows**: Use double quotes and fix sed
  ([`2c1e8fd`](https://github.com/TourmalineCore/c2pie/commit/2c1e8fd7cb42e86368b69b1229354d2d3b4fe866))

### Documentation

- **readme**: Bring test coverage score up to date
  ([`b93c02a`](https://github.com/TourmalineCore/c2pie/commit/b93c02a205e7ebadea617a338ca6f738c9f001c2))

- **readme**: Bring test coverage score up to date
  ([`fe416f7`](https://github.com/TourmalineCore/c2pie/commit/fe416f75d8e9b4f5696e9f7fe3d337f160ec7ed7))

- **readme**: Bring test coverage score up to date
  ([`abbe3d2`](https://github.com/TourmalineCore/c2pie/commit/abbe3d2a634cde0dc0551d0408934691efe6f145))

- **readme**: Change links to banner
  ([`3ce2606`](https://github.com/TourmalineCore/c2pie/commit/3ce26060905d8acc0f13dcfa241dc3b379e4c95c))

- **readme**: Fix incorrect badge rendering
  ([`95de4ec`](https://github.com/TourmalineCore/c2pie/commit/95de4ec92b3dd99fb8d9a4e1e4f0cb348048740c))

- **readme**: Fix invalid linking
  ([`6aab921`](https://github.com/TourmalineCore/c2pie/commit/6aab9216c9341e0d9fadc86eaf664769172c30a1))

- **readme**: Fix not complete url
  ([`24b768d`](https://github.com/TourmalineCore/c2pie/commit/24b768db20a749e120a5aa5cb8a2be874fecb614))

- **readme**: Fix url to badge
  ([`f263901`](https://github.com/TourmalineCore/c2pie/commit/f2639018a511c28a5255d52a7a7a953d7e41a76f))

### Features

- **semantic-release**: Exclude workflows commits from changelog
  ([`7df9427`](https://github.com/TourmalineCore/c2pie/commit/7df9427c21bc7a2e832c71bb026f155714cdb6d1))

- **workflows**: Add badge color replacement
  ([`e249736`](https://github.com/TourmalineCore/c2pie/commit/e249736f15c0b3c0f8d8f3ec5510dd1ae657462a))

- **workflows**: Update coverage badge dynamically
  ([`8554847`](https://github.com/TourmalineCore/c2pie/commit/85548474f7c415b7f811081af03e7d99ea3d90f9))

### Refactoring

- **workflows**: Add comments to steps
  ([`9ab3912`](https://github.com/TourmalineCore/c2pie/commit/9ab391257ef3c4b6fd2ae1b916ab7e14ec8a048b))

- **workflows**: Move git operations to a separate step
  ([`267683b`](https://github.com/TourmalineCore/c2pie/commit/267683b384dbfbd94b29a80c5ca48e16cc17d4b5))

- **workflows**: Use better name for a job
  ([`bb88ee3`](https://github.com/TourmalineCore/c2pie/commit/bb88ee33f4bb84a62366456149175636e4b8e4b5))


## v0.1.0-alpha.3 (2025-10-14)

### Bug Fixes

- **workflows**: Add name to artifact
  ([`29a08cf`](https://github.com/TourmalineCore/c2pie/commit/29a08cf890b4f8cabe4b1cd35386ffedbdbb1569))

### Features

- **workflows**: Remove multi-platform build
  ([`c7cb49e`](https://github.com/TourmalineCore/c2pie/commit/c7cb49e644aa93b40714d66598fe3dd290937510))


## v0.1.0-alpha.2 (2025-10-14)

### Bug Fixes

- **c2pie**: Replace manifest label value with urn:uuid
  ([`7249501`](https://github.com/TourmalineCore/c2pie/commit/7249501d8743747012620ffb4fc3b606d79e88d1))

- **tests**: Add sample jpeg
  ([`ebd91d2`](https://github.com/TourmalineCore/c2pie/commit/ebd91d29757e272c0c7c1849ed120865802facc5))

- **workflows**: Add cargo-install cache-key inside rust cache action
  ([`32069c8`](https://github.com/TourmalineCore/c2pie/commit/32069c899b30f0a250eb67e538b33d36e2d53aaf))

- **workflows**: Define bash as default shell
  ([`bfda110`](https://github.com/TourmalineCore/c2pie/commit/bfda11072884019892e3a01049696be7476e3bcd))

- **workflows**: Fix coverage still skipping
  ([`14a09d3`](https://github.com/TourmalineCore/c2pie/commit/14a09d35525a13c93845b9ab4e8518864720ad18))

- **workflows**: Fix poetry not found on windowa
  ([`cb55887`](https://github.com/TourmalineCore/c2pie/commit/cb558870f894ea144681cf10059884c1e7d6a1da))

- **workflows**: Move run command to a separate step
  ([`7d6bd96`](https://github.com/TourmalineCore/c2pie/commit/7d6bd960ce25f3431f8ff96e83186d7b410fc433))

- **workflows**: Move to github runners from self-hosted
  ([`184d319`](https://github.com/TourmalineCore/c2pie/commit/184d3196d984622c5bb58600c2229cda52a58f28))

- **workflows**: Remove extra rust caching
  ([`13e8e4c`](https://github.com/TourmalineCore/c2pie/commit/13e8e4c5a895f0c8ca5da165d1d22b169c3c7487))

- **workflows**: Remove space
  ([`4585f3a`](https://github.com/TourmalineCore/c2pie/commit/4585f3adaea8d7000cfe3a187195ca9e920e05ff))

- **workflows**: Remove unnecessary condition
  ([`e83be02`](https://github.com/TourmalineCore/c2pie/commit/e83be0246970737f260401366d0c3a028519cc47))

- **workflows**: Use another action version
  ([`947edc5`](https://github.com/TourmalineCore/c2pie/commit/947edc5dd3cc1dfad64e887671690baeff47a3d0))

- **workflows**: Use cargo-install action instead of manual installation
  ([`e23ce3e`](https://github.com/TourmalineCore/c2pie/commit/e23ce3e7a3aeb19678d908657a31402632928b09))

- **workflows**: Use updated lint and test workflow
  ([`4cbfd4f`](https://github.com/TourmalineCore/c2pie/commit/4cbfd4ff2c316728b8e66391f85fcf58b42548ce))

### Documentation

- **readme**: Add badge with c2pa version
  ([`2b4c974`](https://github.com/TourmalineCore/c2pie/commit/2b4c974b1eac397c9576bb0c8d344cba3ef79572))

- **readme**: Add c2pa version and style quotes
  ([`249fbb1`](https://github.com/TourmalineCore/c2pie/commit/249fbb1cb14fa2dc5e8ae6ab9fd3560f553eda47))

- **readme**: Add coverage badge
  ([`128b3dc`](https://github.com/TourmalineCore/c2pie/commit/128b3dcafe91fe439ed20dce3ae307fde5b24feb))

- **readme**: Minor tweaks
  ([`c3cc030`](https://github.com/TourmalineCore/c2pie/commit/c3cc030fe045a4ba8cfbb45bf94106f50638b240))

- **readme**: Remove coverage badge
  ([`924dc22`](https://github.com/TourmalineCore/c2pie/commit/924dc221b1a7408e1e8cc63900106bd9188d589f))

- **readme**: Replace manifest labels in validation example
  ([`2b7e686`](https://github.com/TourmalineCore/c2pie/commit/2b7e686ef05e04a6ca7767511991cc36e2fb43bb))

### Features

- **pyproject**: Add readme, license and python requirement
  ([`be41336`](https://github.com/TourmalineCore/c2pie/commit/be41336f92f79222960261d91bce61bfbe786c43))

- **pyproject**: Disable build for sem-rel and update commit parsing
  ([`5aa3122`](https://github.com/TourmalineCore/c2pie/commit/5aa31228bcd205c15c79581c9a66115945a7f179))

- **workflows**: Add support for multi-platform distribution
  ([`85c002e`](https://github.com/TourmalineCore/c2pie/commit/85c002e63617629039e2600ecb4bec3a18e7560f))

- **workflows**: Make coverage job not skip if some tests weren't successful
  ([`36f6904`](https://github.com/TourmalineCore/c2pie/commit/36f690408bdd3d73db5e996d228608f32d10c77f))


## v0.1.0-alpha.1 (2025-10-10)

- Initial Release
