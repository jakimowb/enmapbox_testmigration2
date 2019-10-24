# EnMap-Box Contributor Guidelines
The EnMAP-Box is a freely available, platform-independent software designed to process hyperspectral remote sensing data, 
and particularly developed to handle data from the EnMAP sensor. It is provided as a plug-in for QGIS.

# Repository

The central and public repository of the software produced for official EnMap-Box products (versions, releases etc.) 
are hosted completely at https://bitbucket.org/hu-geomatics/enmap-box and once approved as QGIS plugin referenced at 
https://plugins.qgis.org/plugins/enmap-box and other places.

# Contributions

Contributions such as source code, documentation or any other creative work cannot be committed by anyone to the 
central repository. Commit rights are given to maintainers and approved contributors. 
Contributions from other individuals must be provided as pull requests or in similar ways that require the compliance 
with certain rules and the review by the maintainers following these rules and further checklists.

## Maintainers

 tbd.

## Contributors
 
 tbd.
 
## Licensing

The software produced for the EnMAP-Box is licensed according to the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of the License (SPDX short identifier: GPL-3.0), or 
(if desired) any later version. See either https://www.gnu.org/licenses/gpl-3.0.en.html or 
https://opensource.org/licenses/GPL-3.0 for further details of the license.

## Applying License Terms

If possible, each file of a contribution to the central repository must include a notice. It is safest to attach the 
notice to the start of each file to most effectively state the exclusion of warranty; and each file should have at 
least the copyright line and a pointer to where the full notice is found.

```
The EnMAP-Box is a freely available, platform-independent software designed to process hyperspectral remote sensing data,
and particularly developed to handle data from the EnMAP sensor. 

This file <does this and that>.

Copyright (C) <year>  
<name of author> (<acronym of employer>, <email address>), 
<name of author> (<acronym of employer>, <email address>), 
<name of author> (<acronym of employer>, <email address>),
...
<name of employer> (<acronym of employer>, <website URL if employer>), 
<name of employer> (<acronym of employer>, <website URL if employer>), 
<name of employer> (<acronym of employer>, <website URL if employer>), 
...

Parts of this program (especially the <code for whatever>) 
were developed within the context of the following publicly funded
Projects and or measures:
- <project name>, <funding agency, grant, programme>, Grant Agreement <number> (<website URL>)
- ...

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

Add information for text marked by `< ... >`.

# Contributor License Agreements (CLA)
The purpose of CLAs are to clearly define the terms under which intellectual property has been contributed to the 
EnMap-Box and thereby allow us to defend the project should there be a legal dispute regarding the software at some future time.


## Individual Contributor License Agreement (ICLA)
The EnMap-Box Consortium desires that all maintainers and contributors of ideas, code, or documentation to the EnMap-Box 
project complete, sign, and submit an ICLA. A signed ICLA is required to be on file before an individual is given 
commit rights to the EnMap-Box repository. The ICLA form for filling and signing is available at 
https://www.apache.org/licenses/icla.pdf.

The ICLA is not tied to any employer, so it is recommended to use one's personal information, e.g. for email address in 
the contact details, rather than an email address provided by an employer.

## Corporate Contributor License Agreement (CCLA)
For a corporation that has assigned employees to work on the EnMap-Box, a CCLA is available for contributing 
intellectual property via the corporation, that may have been assigned as part of an employment agreement.

Note that a CCLA does not remove the need for every developer to sign their own ICLA as an individual, which covers 
both contributions which are owned and those that are not owned by the corporation signing the CCLA.

The CCLA legally binds the corporation, so it must be signed by a person with authority to enter into legal contracts 
on behalf of the corporation. The CCLA form for filling and signing is available at http://www.apache.org/licenses/cla-corporate.pdf.

## Submitting License Agreements
Documents may be submitted by email and signed by hand or by electronic signature. 
The files should be named icla.pdf and icla.pdf.asc for individual agreements; ccla.pdf and ccla.pdf.asc 
for corporate agreements. Zip files, other archives, or links to files are not accepted. 
The files must be attached to the mail.

When submitting by email, please fill the form with a pdf viewer, then print, sign, scan all pages into a single pdf file, 
and attach the pdf file to an email to cla@enmap.org. If possible, send the attachment from the email address in the document. 
Please send only one document per email.

If you prefer to sign electronically, please fill the form, save it locally (e.g. icla.pdf), and sign the file by 
preparing a detached PGP signature. For example, gpg --armor --detach-sign icla.pdf

The above will create a file icla.pdf.asc. Send both the file (icla.pdf) and signature (icla.pdf.asc) as attachments 
in the same email. Please send only one document (file plus signature) per email. Please do not submit your public key. 
Instead, please upload your public key to pgpkeys.mit.edu.

## Developer Certificate of Origin (DCO)
Contributors who have not signed an ICLA are in a somewhat fuzzy spot. If they make a large contribution, 
or many contributions, then the EnMap-Box maintainers will likely ask to submit an ICLA. 
However, for small fixes, infrequent and other minimal or sporadic contributions the terms for licensing 
and intellectual property still must be clarified.

For this purpose, barriers for contributing are minimized and contributors pinky swear that they're submitting their own 
work or rather certify that they adhere to the requirements of the DCO defined in version 1.1 or later at 
https://developercertificate.org/ by signing-off their pull requests or similar ways of contributing .

The DCO is very Git-centric, and it only relies on commit metadata. Indeed, signing-off a commit is just about 
appending a Signed-off-by: line in the commit comment as in:

````
commit b2c150d3aa82f6583b9aadfecc5f8fa1c74aca09

Modify various document (man page) files to explain
in more detail what --signoff means.

This was inspired by https://lwn.net/Articles/669976/ where
paulj noted, "adding [the] '-s' argument to [a] git commit
doesn't really mean you have even heard of the DCO...".
Extending git's documentation will make it easier to argue
that developers understood --signoff when they use it.

Signed-off-by: David A. Wheeler <dwheeler@dwheeler.com>
Signed-off-by: Junio C Hamano <gitster@pobox.com>
````

Even this approach introduces a low barrier for contributions, it is very easy to use whatever email address you want 
for a commit, and the sign-off is just text. Since the issue of trust is important the use of GnuPG signatures in Git 
commits is recommended additionally, e.g. with:

````
git commit -s -S (makes GnuPG-signed commits, and)
git log --show-signature (shows GnuPG signatures in the log history)
git merge --verify-signatures branch (ensures that all commits are signed and valid before performing a merge)
````

Having to use GnuPG for all commits can be a bit daunting. Perhaps a simple alternative can be to require that 
contributors add their name and email to a file (e.g., CONTRIBUTORS), and do so with a GnuPG + signed-off commit, 
and later at least sign-off commits.






