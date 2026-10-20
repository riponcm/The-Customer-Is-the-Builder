[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0) [![État de la traduction](https://hosted.weblate.org/widget/signature-pdf/application/svg-badge.svg)](https://hosted.weblate.org/engage/signature-pdf/) [![Docker Pull](https://img.shields.io/docker/pulls/xgaia/signaturepdf)](https://hub.docker.com/r/xgaia/signaturepdf) [<img src="https://install-app.yunohost.org/install-with-yunohost.svg" alt="Install Signaturepdf with YunoHost" style="height:20px" />](https://apps.yunohost.org/app/signaturepdf)
# Signature PDF

![Logo signature PDF](https://github.com/24eme/signaturepdf/blob/master/public/logo.svg)

Free web software for signing (alone or with others), organizing (merge, sort, rotate, delete, extract pages, ...), editing metadatas or compressing PDFs.

## Instances
List of instances where you can use this software:
- [pdf.24eme.fr](https://pdf.24eme.fr) (by [24eme](https://www.24eme.fr/services-libres/))
- [pdf.libreon.fr](https://pdf.libreon.fr) (by [Libreon](https://libreon.fr/))
- [signature.pdf.hostux.net](https://signature.pdf.hostux.net) (by [Hostux](https://hostux.network/))
- [pdf.nebulae.co](https://pdf.nebulae.co) (by [Nebulae](https://nebulae.co/))
- [pdf.kaosx.ovh](https://pdf.kaosx.ovh)
- [pdf.ti-nuage.fr](https://pdf.ti-nuage.fr) (by [Ti Nuage](https://www.ti-nuage.fr/))
- [pdf.cemea.org](https://pdf.cemea.org) (by [Les Ceméa](https://mallette.cemea.org))
- [pdf.caph.info](https://pdf.caph.info) (by [caph.info](https://caph.info))
- [pdf.spirio.fr](https://pdf.spirio.fr) (by [Spirio.fr](https://spirio.fr/))
- [pdf.sequanux.org](https://pdf.sequanux.org) (by [Sequanux](https://www.sequanux.org/))
- [pdf.deblan.org](https://pdf.deblan.org) (by [Deblan](https://wiki.deblan.org/hosting/overview/))
- [pdf.ouvaton.coop](https://pdf.ouvaton.coop) (by [OUVATON](https://ouvaton.coop/))
- [signpdf.liber-it.fr](https://signpdf.liber-it.fr) (by [Liber-IT](https://site.liber-it.fr/))
- [signaturepdf.linux07.fr](https://signaturepdf.linux07.fr) (by [Linux07](https://linux07.fr/))
- [signpdf.blablalinux.be](https://signpdf.blablalinux.be) (by [Blabla Linux](https://blablalinux.be/))
- [framapdf.org](https://framapdf.org/home) (by [Framasoft](https://framasoft.org))
- [pdf.s2s.video](https://pdf.s2s.video) (by [s2s](https://www.s2s.video))


_Feel free to add yours through an issue or a pull request._

## License
Open-source software under the AGPL V3 license.

## Table of Contents

- [Installation](#installation)
    - [Debian/Ubuntu](installation.md#debian-ubuntu)
    - [Docker](installation.md#deploy-with-docker)
    - [Linux Alpine](installation.md#alpine)
    - [Package](installation.md#package)
- [Configuration](#configuration)
    - [Enabling and Configuring Multi-Signature Mode](#enabling-and-configuring-multi-signature-mode)
    - [Disabling the Organize Mode](#disabling-the-organize-mode)
    - [Hiding or Modifying the Demo PDF Link](#hiding-or-modifying-the-demo-pdf-link)
    - [Customize the CSS](#customize-the-css)
    - [Custom retention period for shared PDF](#custom-retention-period-for-shared-pdf)
    - [Default Fields for Metadata Editing](#default-fields-for-metadata-editing)
- [Update](#update)
- [Tests](#tests)
- [Libraries Used](#libraries-used)
- [Contributions](#contributions)
- [Screenshots](#screenshots)

## Installation

- [Debian/Ubuntu](installation.md#debian-ubuntu)
- [Docker](installation.md#deploy-with-docker)
- [Linux Alpine](installation.md#alpine)
- [Package](installation.md#package)

## Configuration

### Enabling and Configuring Multi-Signature Mode

This mode allows multiple people to sign a PDF, but it requires that the PDFs be stored on the server.

It is not mandatory to enable this mode for the application to work; it is an option.

Create the `config/config.ini` file

```
cp config/config.ini{.example,}
```

In the `config/config.ini` file, configure the `PDF_STORAGE_PATH` variable with the path where uploaded PDF files can be stored:

```
PDF_STORAGE_PATH=/path/to/folder
```

Create this folder:

```
mkdir /path/to/folder
```

The web server should have write permissions on this folder.

For example, for Apache:

```
chown www-data /path/to/folder/to/store/pdf
```

You can enable PDFs to be stored encrypted on the server with a symmetric key known only to the signers.

To activate it, gpg needs to be installed and option PDF_STORAGE_ENCRYPTION must be set to true.

In the `config/config.ini` file :

```
PDF_STORAGE_ENCRYPTION=true
```

### Enabling digital signature

The digital signature depends on `pdfsig` from the poppler project (poppler-utils debian package) and `certutil` from libnss3 project (libnss3-tools debian package).

On debian :

```
sudo apt-get install poppler-utils libnss3-tools
```

To enable digital signature, create certificates in a NSS database. The shell script `create_nss_certs.sh` in `tools` helps to do it :

     bash tools/create_nss_certs.sh NSS_DIRECORY/ MY_NSS_PASSWORD MY_CERT_NICK MY_SIGNATUREPDF_URL

Once created, set the following directives in the `config/config.ini` file.

    NSS3_DIRECTORY=NSS_DIRECORY/
    NSS3_PASSWORD="MY_NSS_PASSWORD"
    NSS3_NICK="MY_CERT_NICK"

You must then set the rights on the nss folder and its contents so that the web server has read access to it.

For example with apache on debian :

```
chown www-data:www-data -R NSS_DIRECORY
```

### Disabling the Organize Mode

To disable the Organize mode, add `DISABLE_ORGANIZATION=true` to the
`config/config.ini` file.

### Hiding or Modifying the Demo PDF Link

To hide the demo PDF link, add `PDF_DEMO_LINK=false` to the
`config/config.ini` file.

### Customize the CSS

It's possible to add a custom CSS file to the location `public/css/app-specific.css`.

If this file exists, it will be loaded automatically.


### Custom retention period for shared PDF

In `config/config.ini` file activate these options :

```
[signature]

; Enable custom retention period for shared PDF
; Thi