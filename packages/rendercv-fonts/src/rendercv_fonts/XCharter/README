				XCharter Fonts
				Michael Sharpe

This package is an extension of Bitstream Charter, whose original license is reproduced below, as required under the terms of that license. The extension provides small caps, oldstyle figures and superior figures in all four styles, accompanied by LaTeX font support files. The font files themselves are  in otf and pfb formats. The fonts are licensed as Free fonts under the same terms as the original from Bitstream. All other support files are subject to the LaTeX Project Public License. See 
http://www.ctan.org/license/lppl1.3
for the details of that license. 

Original Bitstream Free font license:

  (c) Copyright 1989-1992, Bitstream Inc., Cambridge, MA.

  You are hereby granted permission under all Bitstream propriety rights
  to use, copy, modify, sublicense, sell, and redistribute the 4
  Bitstream Charter (r) Type 1 outline fonts for any purpose and without
  restriction; provided, that this notice is left intact on all copies
  of such fonts and that Bitstream's trademark is acknowledged as shown
  below on all unmodified copies of the 4 Charter Type 1 fonts.

    BITSTREAM CHARTER is a registered trademark of Bitstream Inc.

Portions of the font modifications are Copyright (c) 2009--2012, Andrey Panov; Copyright (c) 2013--2024, Michael Sharpe.


Current version 1.26 2024-06-18

(Several new features described in the documentation remain incomplete until a new version of newtx adds the necessary underpinnings.)

Changes in version 1.26
1. Corrected the slope of italic and bold italic small caps.
2. Minor documentation changes.

Changes in version 1.25
1. Corrected the misrendering of oldstyle 1 under the option osf.
2. Corrected some errors in the generating scripts that led to numerous corrections and additions to the rendering of figures.

Changes in version 1.24
1. Changes to XCharter.sty, with thanks to Marei Peischl for signalling the problems and suggesting the solutions:
	(i) Moved the definition of \familydefault from the \AtEndPreamble hook, which made it impossible to change;
	(ii) Prevented the loading of the T1 encoding is cases where it was not required.
2. Other changes to XCharter.sty: new option otfmath (loads XCharter-Math), notextnu (prevents XCharter.sty from changing definition of \textnu in babel[greek]); added \textnum as replacement for \textnu.

Changes in version 1.23
1. Added the {t1,ot1,ly1} minxcharter fd files, needed for loading from newtx.
2. Substantial changes to XCharter.sty so that it now works with all latex engines.

Changes in version 1.224
Added definitions of \nustyle and \destyle to XCharter.sty.

Changes in version 1.224
Added glyphs for U+02BE, U+02BF, U+02D2, U+02D3: modifier letters for half ring shapes, useful to some linguists.

Changes in version 1.223
Removed the twelve spurious vf files XCharter1-*-tosf-t2a*.vf which were leading to  recursion errors in T2A with old style figures.

Changes in version 1.222
1. Corrected the Bold Italic Greek math font so that epsilon and varepsilon are no longer interchanged. (Thanks Holger Gerhardt.)
2. Renamed \textin to \textinf (denominator figures) so as not to conflict with hyperref usage.

Changes in version 1.221
Removed a number of empty tfm files and references to them in some fd files.

Changes in version 1.22 (never distributed)
Added a theorem font along the lines of those in newtx and newpx, using a separate font family XCharterTH.

Changes in version 1.216
Removed a superfluous line from XCharter that was interfering with choice of bold in other faces.


Changes in version 1.215
Some t2a encoded tfm files were omitted due to a processing error. Now fixed.

Changes in version 1.214
Brought math blackboard bold alphabets into conformance with additions to newtxmath.


Changes in version 1.213
1. Corrected the generating script to eliminate an embarrassing number of errors and missing files in the previous two updates.
2. Corrected behavior of \textosfI macro.

Changes in version 1.212
Corrected versions of otf and pfb files. (Some of those lacked the updates announced in 1.211.)

Changes in version 1.211
1. Added 6 new glyphs:
	bullet operator	U+2219 (the glyph is a copy of uni2027, HYPHENATION POINT)
	integral		U+222B
	lessequal		U+2264
	greaterequal	U+2265
	lozenge			U+25CA
	uni2423			U+2423 (open box)
2. The visiblespace glyph in T1 slot 32 was replaced by uni2423.

Changes in version 1.210
Corrected sty file in accordance with 2020 latex incorporation of mweights.

Changes in version 1.209
Corrected the \textcircled macro so that it scales as expected.

Changes in version 1.208
Added a no-break space (U_00A0) to each style. (Unicode TeX uses this to render ~.)

Changes in version 1.207
1. The last update broke much of the t2a support. That is corrected in this update.
2. Added alternate one.oldstyle in the text companion (ts1) font.

Changes in version 1.206
1. Added many new glyphs so that coverage of the TS1 encoding is essentially complete.
2. Added many new superscript letters and symbols.
3. Added i.TRK and i.TRKsc with a localization lookup and an added c2sc entry for Turkish language (latn/TRK) users.
4. Added a new \textcircled macro to the sty file.
5. Improved the \textfrac macro.

Changes in version 1.205
Replaced the otf files, some of which had corrupted feature lookups.

Changes in version 1.204
1. Added the missing Dcroat glyphs in the otf files. 
2. Added Greek glyphs designed earlier for math use as text glyphs in the otf files. Currently, these are available only in Roman, Italic, Slanted and Bold, but the only ones with reasonably proper text spacing are Roman and Italic. These are not yet available to LaTeX users.
3. For reasons I do not understand, with the current version of fontspec, loading XCharter with option Numbers={OldStyle} does not work, but RawFeature={+onum} does.

Changes in version 1.203
1. Corrected a bad LIGKERN entry affecting the >> ligature in t2 encodings.
2. Modified the math italic and bold math italic v and w to be more shapely. 
3. Added a variant for of math italic and bold math italic y. These may be chosen using the alty option to newtxmath/charter.
(Thanks Fabien Guillemot for suggestions concerning the last two items.)

Changes in version 1.202
Removed some tfm files which were duplicates of some in newtx.

Changes in version 1.201
Changed name of subscript adjustments file from xcharter.subs to newtx-xcharter-subs.tex.

Changes in version 1.20
The mathematical parts of fonts have been enhanced so that, when used with newtxmath, they can produce pdf files that satisfy PDF/A-1b. See the newtxmath documentation for details. Note that \hslash, \hbar, \lambdaslash and \lambdabar are now built from Charter glyphs.

Changes in version 1.122
1. Added many accented glyphs, so that XCharter can now be used to produce Romanized forms of Sanskrit, Tamil and Vietnamize, as well as other European languages.
2. Modified a number of kerning pairs.

Changes in version 1.121
Added mark to mark tables so that in unicode text processing, single diacritics are correctly drawn even if there is no precomposed glyph.

Changes in version 1.12
1. Added new glyphs for Sharp-s and its small caps version as well as a new feature, ss01, to control whether to use these forms in unicode processing. 
2. Added feature cv01 to control shape of oldstyle "one" in unicode processing.
3. Added kerning for parens and brackets as well as for some unusual letter combinations.

Changes in version 1.116
1. Corrected some kerns between quotesinglbase---U+201A (resp., quotedblbase---U+201E) and A, X. (Thanks to Ulrich Büchsel.)
2. The ot2 encoded Cyrillic are now working correctly again.
3. Some math mode tfm/vf matching errors are now fixed.

Changes in version 1.115
Version 1.114 turned out to lack close to twenty essential files, thanks to an error in my generating script. Now corrected. (Thanks to Leonid Sinev.)


Changes in version 1.114
1. Substituted the pfb fonts produced directly from FontForge for those constructed by otftotfm. The former seem to work better in the production of PDF/A-1B documents. 
2. Reworked the T2A fonts, which had fallen into disrepair, some not handling the basic ligatures correctly. These now work again as expected.

Changes in version 1.113
Added new math italics with original Charter italic v and w. Not suited for use with Greek math \nu.

Changes in version 1.112
1. Reworked the organization of math alphabets to use unicode names.
2. Small changes to some glyph shapes and metrics.

Changes in version 1.111
Minor changes to some Greek glyph shapes.

Changes in version 1.11
1. Addition of Greek math letters in style matching XCharter.
2. Changed the math alphabets used by newtxmath with charter option so as to use the new Greek letters.

Changes in version 1.102
Kerning changes affecting L and its variants followed by double or single quotes.

Changes in version 1.101
1. Corrected math spacing for period and comma under xcharter option to newtxmath.
2. Minor spacing changes to math v and w.

Changes in version 1.1
Added support for Serbian Cyrillic typesetting in XeLaTeX, LuaLaTeX and pdflatex.

Changes in version 1.093
1. Modified handling of the sups option when using KOMA classes.
2. Changed \textnu to \textnumerator to avoid conflict with babel greek, though \textnu will be available as an abbreviation in other cases. (Thanks, Enrico Gregorio.)

Changes in version 1.093
Corrected OT1XCharter-TLF.fd, missing Greek in update to 1.09.

Changes in version 1.092
Restored XCharter-Bol-osf.tfm, inadvertently omitted from v. 1.091.

Changes in version 1.091
Corrected errors (introduced in version 1.09) in fd files.

Changes in version 1.09
1. Added Cyrillic and some figure styles from Andrey Panov's Khartiya, and created LaTeX support files for OT2 and T2A encodings.
2. Created slanted versions of the fonts and modified the fd files accordingly.
3. Added figure styles numerators, denominators, inferiors.
4. Added scosf option to specify use of oldstyle figure in Small Caps.
5. Added \textfrac macro for fractions.

Changes in version 1.08
Modified the sty file so that XCharter text figure styles are selected always in the \AtEndPreamble hook. (Formerly, using babel would prevent this.)

Changes in version 1.079
Added two entries to smcp table so that dotlessi and dotlessj map to correct small cap glyph.

Changes in version 1.078
1. Small spacing and kerning changes.
2. Added uni2016 glyph---required by some footnote macros.

Changes in version 1.077
Modified TTF name in BoldItalic otf from BoldItalic to Bold Italic so that Windows installs it correctly.

Changes in version 1.076
Corrected some issues with the generating script as it affected ot1-encoded tosf fonts.

Changes in version 1.075
Added OT1 encoded fonts with Greek uppercase letters taken from newtx, scaled up appropriately. This addition permits newtxmath with option charter to behave as expected with \mathrm, \mathit, \mathnormal and \mathbf applied to uppercase Greek letters.

Changes in version 1.074
Modified mu in Roman and Bold to have upright shape based on u, so that users of siunitx get the expected form of mu.

Changes in version 1.073a
Corrected typo in sty file. (Thanks Uwe Siart)

Changes in version 1.073
Modified XCharter.sty to detect babel usage and change behavior accordingly. Documentation also modified.

Changes in version 1.072
Modified kerning tables in each style to correct overly tight kerning between letters (especially uppercase) and punctuation. (Thanks Sven Boese.)

Changes in version 1.071
Corrected missing aogonek in XCharter-Bold and missing smcp entries for zdotaccent.sc and zacute.sc in XCharter-Italic. (Thanks Sebastian Wasiuta.)

Changes in version 1.07
1. Added over 50 new glyphs to each style so that the package now covers essentially the complete range of the EC (T1) encoding.
2. Corrected behavior of small cap germandbls when using the alternate form of oldstyle 1.

Changes in version 1.06
Added support files for a new "charter" option to newtxmath, providing math italic (oml) with XCharter [bold-]italic letters replacing Times [bold-]italic, with sizes reduced to match xheight of Times italic.

Changes in version 1.05
1. Slight modifications of control points of some oldstyle figures.
2. Modified kerning tables for P-period, P-comma and P-hyphen in all styles, all existing ones appearing much too tight.
3. Modified documentation to reflect updated usage of osf and osfI.

Changes in version 1.041
Corrected definitions of \useosf and \useosfI.

Changes in version 1.04
Substantial reworking of kerning tables in small caps.
Substantial revision of italic and bold italic oldstyle figures.
Revised method for making support files with alternate form of oldstyle `one'.

Changes in version 1.03
Minor changes to kerning tables in small caps.
Changes to sty file to allow osf deferred until EndPreamble so that math always uses TLF.

Changes in version 1.02
Corrected the code so that there no longer an unwanted space following the footnote marker.

Changes in version 1.01
The method of generating the support files has changed from version 1.00, and is outlined below. The result is that the problem in version 1.00, where under the option oldstyle (or the macro \useosf) the resulting oldstyle 1 (like a short 1) failed to behave as the character 1 when copied from a pdf file, is now rectified.

The otf fonts contain all the kerning and other tables. Should you wish to modify these yourself, the following outline of the method should be followed. 

Place the 4 otf files and the 4 afm files in a new folder along with a subfolder named texmf. Then run the command

/usr/texbin/autoinst  --noupdmap  --noswash --notitling --noornaments --target=./texmf --encoding=TS1,T1,LY1 --vendor=public --typeface=xcharter *.otf

after cding to the new folder. You should replace the newly generated XCharter.sty and .fd files the with the ones from the distribution in order to preserve the functionality of the package. The names of the encoding files should also be modified appropriately from those assigned by autoinst. I used the following bash shell script, which assumed you are in the directory holding the otf files and a texmf subfolder:

#!/bin/bash
pushd texmf/fonts/map/dvips/xcharter
sed -i '' 's/<\[a_/<\[xch_/g' XCharter.map
popd
pushd texmf/fonts/enc/dvips/xcharter
for f in *.enc; do mv ${f} xch${f:1}; done
popd

To make the alternate form of osf `one' available, run the python script altone.py.

Please send comments and bug reports or suggestions for improvement to

msharpe at ucsd dot edu