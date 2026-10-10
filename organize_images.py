import os
import sys
import glob
import re
import shutil
import csv
import json
import argparse
from datetime import datetime

# Full list of prompts in sequential order
PROMPTS = [
    ("[0:00]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a snarling, exaggerated muscle-bound stick figure holding a sword, a thick red diagonal X drawn across the whole scene, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[0:10]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple film clapperboard icon labeled HOLLYWOOD in bold ALL CAPS marker text, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[0:12]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, an old stone tombstone icon and an unrolled scroll beside bold text reading THE REAL RECORD, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[0:18]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a stick figure gladiator standing beside a large money bag icon, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[0:25]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, the same gladiator stick figure standing inside a protective glowing circle outline, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[0:34]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, large bold ALL CAPS red marker text centered reading 7 STAGES, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[0:38]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple bone icon, a tombstone icon, and an unrolled scroll arranged together in a row, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[0:49]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a large yellow question mark over an ordinary stick figure wearing simple chain shackles on its wrists, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[1:00]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, large bold ALL CAPS red marker text centered reading STAGE ONE, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[1:04]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, three small stick figures standing in a row labeled PRISONER, CRIMINAL, and ENSLAVED in bold ALL CAPS marker text, chains on their wrists, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[1:13]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a stick figure wearing a simple toga signing a document at a table, a small coin bag and laurel icon beside it, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[1:27]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a stick figure walking forward along a path toward a distant gate, no weapon in hand yet, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[1:35]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, large bold ALL CAPS red marker text centered reading STAGE TWO, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[1:37]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a stick figure standing before a stone gateway labeled LUDUS, reciting from an unrolled scroll, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[1:44]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, four small icons in a row: a flame, a rope, a raised fist, and a sword, each labeled with a single bold word beneath, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[1:55]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS black marker text reading METAPHOR with a thick red diagonal X drawn across it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[1:57]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple balance scale icon of justice shown broken and tilted, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[2:06]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a ludus owner stick figure holding a leash connected to a gladiator stick figure, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[2:14]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a toga-wearing stick figure signing a document at a table with a worried expression, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[2:20]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, the same stick figure shown half in a toga and half in gladiator armor, a visual swap down the middle of the body, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[2:25]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a small gold coin and a laurel wreath icon held just out of reach of an outstretched stick-figure hand, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[2:30]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a stick figure wearing a toga writing on a scroll labeled RESTRICT in bold ALL CAPS marker text, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[2:43]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a stick figure standing at a fork, one path weighed down by a heavy chain-and-coin icon labeled DEBT, the other leading to an open gate, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[2:51]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, large bold ALL CAPS red marker text centered reading STAGE THREE, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[2:55]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple training-academy building icon with an open courtyard, clearly distinct from a barred prison icon crossed out beside it, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[3:06]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, several stick figures in a training yard swinging oversized wooden practice weapons, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[3:17]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple wooden bowl filled with barley and bean shapes, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[3:20]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, small archaeologist stick figures with brushes excavating bone shapes from the ground, a sign reading EPHESUS beside them, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[3:36]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS golden yellow marker text centered reading BARLEY EATERS, a simple grain-stalk icon beside it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[3:42]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a plate piled with barley and beans beside a crossed-out meat icon, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[3:48]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a stick figure with a slightly rounder, padded silhouette, a yellow arrow pointing to the padding labeled PROTECTIVE LAYER, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[4:02]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a stick figure drinking from a simple cup with small glowing mineral sparkle marks rising from it, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[4:14]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, large bold ALL CAPS red marker text centered reading STAGE FOUR, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[4:16]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, four differently equipped gladiator stick figures standing in a row, each with distinct weapons and armor, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[4:19]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, four small icons arranged in a row: a net, a trident, a round shield, and a short sword, each labeled beneath in bold text, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[4:24]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a lightly armored stick figure holding a weighted net and a trident, labeled RETIARIUS in bold ALL CAPS marker text, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[4:32]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a stick figure wearing a smooth rounded helmet with tiny eye-slits, labeled SECUTOR in bold ALL CAPS marker text, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[4:44]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a heavily armored stick figure with a large shield labeled MURMILLO standing opposite a lighter armored stick figure with a curved blade labeled THRAEX, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[4:55]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS black marker text reading RANDOM with a thick red diagonal X drawn across it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[4:57]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple wooden schedule board showing two different gladiator-type icons deliberately paired together with a connecting line, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[5:11]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a trainer stick figure studying a small chart showing two opposing weapon icons, thoughtful expression, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[5:18]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, large bold ALL CAPS red marker text centered reading STAGE FIVE, solid orange background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[5:23]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple skull icon with bold text beside it reading EVERY MATCH?, a thick red diagonal X beginning to form over it, solid orange background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[5:27]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, the same skull icon now fully crossed out with a bold red diagonal X, solid orange background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[5:30]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a money bag and a small ticket stub icon beside a gladiator stick figure, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[5:36]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple balance scale with the ALIVE side weighed down heavier than the other side, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[5:44]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, three small icons in a row: a raised open hand, two clasped hands in a draw, and a seated sponsor figure pointing, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[5:49]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a gladiator stick figure kneeling with one arm raised in an appeal gesture toward a seated sponsor figure in the stands, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[6:03]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a small skull icon labeled REAL RISK in bold ALL CAPS marker text beside it, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[6:06]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS black marker text reading DEFAULT with a thick red diagonal X drawn across it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[6:10]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a skeptical stick figure with a raised eyebrow, a thought bubble reading STABLE SYSTEM? in bold ALL CAPS marker text, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[6:19]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS red marker text reading IMPOSSIBLE TO BREAK with a thick black diagonal X drawn across it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[6:20]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a calendar reading 73 BCE beside a small kitchen knife icon and a gate labeled CAPUA, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[6:36]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, several stick figures grabbing simple kitchen tools and skewers off a table, breaking through a gate, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[6:46]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a small cluster of stick figures growing into a much larger crowd silhouette moving across a hillside, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[6:51]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a row of small soldier stick figures with spears stepping backward away from a much larger approaching crowd silhouette, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[7:07]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS black marker text centered reading 71 BCE, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[7:12]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a long road icon stretching into the distance lined with small solemn upright marker posts, solid dark grey background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[7:19]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple flat senate building icon with columns, a small worried expression drawn on its steps, dark grey background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[7:25]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple chain icon breaking apart into pieces, bold ALL CAPS text beside it reading PROPERTY, dark grey background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[7:31]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, large bold ALL CAPS red marker text centered reading STAGE SIX, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[7:38]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a secutor stick figure portrait beside a carved stone tombstone icon, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[7:49]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, close-up on the tombstone carved with the bold numbers 34, 21, and 9 in a row, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[7:54]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS golden yellow marker text centered reading MISSIO, a small open hand mercy gesture icon beside it, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[8:03]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS red marker text reading REFUSED FREEDOM with a thick black diagonal X drawn across it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[8:12]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a magnifying glass held up to the tombstone inscription, close inspection, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[8:14]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, the word MISSIO in bold golden yellow text on one side and the word FREEDOM crossed out in red on the other side, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[8:17]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS marker text centered reading NO EXAGGERATION NEEDED, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[8:21]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a calendar reading AGE 30 beside the tombstone icon, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[8:33]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, one glowing golden stick figure standing out among a row of plain grey stick figures, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[8:36]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a wide shot of a small cemetery with many simple grave markers arranged in rows, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[8:42]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold text reading 67 REMAINS beside one grave marker highlighted in gold labeled OLD AGE among many plain ones, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[8:51]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple bone icon with a small healed crack line drawn across it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[8:56]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, the same bone icon now with several layered crack lines drawn over each other, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[9:00]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple skull icon with a small dent mark drawn on one side, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[9:05]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple brain icon with a small warning triangle symbol beside it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[9:14]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a row of small grave markers each with a tiny carved name visible on them, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[9:18]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, close-up on the Flamma tombstone icon again, full carved inscription visible, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[9:22]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, the name DELICATUS carved in bold letters beside the Flamma name on the tombstone, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[9:29]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, two gladiator stick figures clasping hands in friendship, warm expression, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[9:36]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, large bold ALL CAPS red marker text centered reading STAGE SEVEN, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[9:43]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a sponsor stick figure handing a glowing wooden sword icon to a kneeling gladiator stick figure, golden yellow background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[9:55]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a golden yellow checkmark stamped over the wooden sword icon, golden yellow background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[9:57]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, one small glowing wooden sword icon surrounded by many plain crossed steel sword icons, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:03]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, the small cemetery icon from earlier beside a single glowing wooden sword icon, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:12]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS marker text centered reading WHAT DOES IT TELL US?, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:17]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS black marker text reading KINDER with a thick red diagonal X drawn across it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:21]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, the same crossed-out KINDER text shown larger and bolder, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:22]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a simple shackle and chain icon wrapped around a stick figure's wrist, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:25]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a crowd of small stick figures in simple arena stands cheering with raised fists, a gladiator figure performing below, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:35]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS red marker text reading MAXIMUM DEATH with a thick black diagonal X drawn across it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:39]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS golden yellow marker text centered reading MAXIMUM SPECTACLE, several small repeated match-icon symbols arranged beneath it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:51]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, the barley bowl icon from earlier beside a crossed-out word MERCY in bold red marker text, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:53]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS marker text centered reading ASSET MANAGEMENT, a small ledger-and-coin icon beside it, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:55]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, the word MISSIO in bold text beside a crossed-out word KINDNESS in red marker text, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[10:57]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a small coin icon forming a protective shell around a gladiator stick figure, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[11:01]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a quiet, still gladiator stick figure silhouette standing alone, the word MYTH fading away in faint outline above it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[11:08]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS red marker text reading END HIS LIFE with a thick black diagonal X drawn across it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[11:11]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a gladiator stick figure performing in the arena with a cheering crowd, the scene slowly fading toward the edges of the frame, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[11:19]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a split frame showing a dramatic movie-poster-style gladiator figure on one side and a plain ordinary stick figure on the other, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[11:23]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, bold ALL CAPS red marker text reading DRAMATIC DEATH with a thick black diagonal X drawn across it, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[11:27]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a gladiator stick figure falling, then standing back up again, shown in a simple repeating circular arrow cycle, tan background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
    ("[11:43]", "Hand-drawn 2D doodle cartoon animation, flat colors, bold black outlines, slightly imperfect sketchy marker lines, a single gladiator stick figure standing quietly, slowly fading into a soft shadow silhouette, white background, no gradients, no shadows, no textures, no photorealism, no 3D, 16:9 aspect ratio, educational YouTube explainer doodle style. Do not render the timestamp text."),
]

# Failed prompts that must be skipped by default (empty for new projects)
SKIPPED_TIMESTAMPS = set()

def parse_prompts_from_text(raw_text):
    """
    Parses arbitrary prompt text containing [mm:ss] or [m:ss] timestamps.
    Supports multiline descriptions for each prompt.
    """
    pattern = r'(\[\d{1,2}:\d{2}\])\s*(.*?)(?=(\[\d{1,2}:\d{2}\])|\Z)'
    matches = list(re.finditer(pattern, raw_text, re.DOTALL))
    prompts = []
    if matches:
        for m in matches:
            ts = m.group(1).strip()
            text = m.group(2).strip()
            text = re.sub(r'\s+', ' ', text)
            if text:
                prompts.append((ts, text))
    else:
        # Fallback: line-by-line
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        for idx, line in enumerate(lines):
            ts_match = re.match(r'^(\[?\d{1,2}:\d{2}\]?)\s*(.*)$', line)
            if ts_match:
                ts = ts_match.group(1)
                if not ts.startswith("["):
                    ts = f"[{ts}]"
                text = ts_match.group(2).strip()
            else:
                ts = f"[{idx+1:02d}]"
                text = line
            text = re.sub(r'\s+', ' ', text)
            prompts.append((ts, text))
    return prompts

def format_prompts_to_text(prompts_list):
    """
    Formats a list of (timestamp, prompt) tuples into standard prompt text blocks.
    """
    return "\n\n".join(f"{ts} {text}" for ts, text in prompts_list)

def load_prompts(source_dir=None):
    """
    Loads prompts from current_prompts.json if available,
    otherwise falls back to default PROMPTS.
    """
    search_dirs = []
    if source_dir:
        search_dirs.append(source_dir)
    search_dirs.append(os.path.dirname(os.path.abspath(__file__)))
    search_dirs.append(os.getcwd())
    
    for d in search_dirs:
        json_file = os.path.join(d, "current_prompts.json")
        if os.path.exists(json_file):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    prompts = [(item["timestamp"], item["prompt"]) for item in data if "timestamp" in item and "prompt" in item]
                    if prompts:
                        return prompts
            except Exception as e:
                print(f"Warning: Failed to load {json_file}: {e}")
    return PROMPTS

def save_prompts(prompts_list, target_path=None):
    """
    Saves a list of (timestamp, prompt) tuples to current_prompts.json.
    """
    if target_path is None:
        target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_prompts.json")
    data = [{"timestamp": ts, "prompt": text} for (ts, text) in prompts_list]
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sanitize_filename(text, prefix, ext=".jpg", max_total_len=180):
    """
    Sanitizes prompt text into a safe Windows filename.
    Removes forbidden characters: < > : \" / \\ | ? *
    Trims to word boundary to fit comfortably within Windows path limits.
    """
    # Extract only the first sentence before instructions
    first_sentence = text.split("Do not render the timestamp text")[0].strip().rstrip(".")
    # Remove Windows invalid filename characters
    clean_text = re.sub(r'[<>:"/\\|?*]', '', first_sentence)
    
    # Calculate available characters for text
    max_text_len = max_total_len - len(prefix) - len(ext)
    if len(clean_text) > max_text_len:
        # Cut at word boundary
        truncated = clean_text[:max_text_len].rsplit(" ", 1)[0].rstrip(" ,.")
    else:
        truncated = clean_text.rstrip(" ,.")
        
    return f"{prefix}{truncated}{ext}"

def organize_images(source_dir, output_folder_name="organized_images", action="copy", archive_originals=True, archive_folder_name="original_images", dry_run=False, prompts=None, skipped_timestamps=None):
    output_dir = os.path.join(source_dir, output_folder_name)
    archive_dir = os.path.join(source_dir, archive_folder_name) if archive_folder_name else None
    
    if prompts is None:
        prompts = load_prompts(source_dir)
    if skipped_timestamps is None:
        skipped_timestamps = SKIPPED_TIMESTAMPS
    
    # 1. Gather image files in the source directory (excluding subdirectories)
    image_patterns = ["*.jpg", "*.jpeg", "*.png"]
    image_files = []
    for pattern in image_patterns:
        for f in glob.glob(os.path.join(source_dir, pattern)):
            if os.path.isfile(f):
                # Ensure we don't pick up files inside output or archive dirs if nested
                f_dir = os.path.normpath(os.path.dirname(f))
                if f_dir != os.path.normpath(output_dir) and (not archive_dir or f_dir != os.path.normpath(archive_dir)):
                    image_files.append(f)
                
    if not image_files:
        print(f"Error: No images found in {source_dir}")
        return False
        
    # 2. Sort images chronologically by modification time (or creation time)
    image_files.sort(key=lambda f: os.stat(f).st_mtime)
    print(f"Found {len(image_files)} images in '{source_dir}'")
    
    # 3. Filter valid prompts by excluding skipped timestamps
    valid_prompts = [(ts, text) for (ts, text) in prompts if ts not in skipped_timestamps]
    print(f"Filtered prompt list has {len(valid_prompts)} prompts (skipped {len(skipped_timestamps)} failed: {skipped_timestamps})")
    
    if len(image_files) != len(valid_prompts):
        print(f"Warning: Count mismatch! Found {len(image_files)} images but have {len(valid_prompts)} valid prompts.")
        if len(image_files) > len(valid_prompts):
            print(f"Only the first {len(valid_prompts)} images will be renamed.")
            image_files = image_files[:len(valid_prompts)]
        else:
            print(f"Only the first {len(image_files)} prompts will be mapped.")
            valid_prompts = valid_prompts[:len(image_files)]
            
    # 4. Prepare output and archive directories
    if not dry_run:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Target directory: '{output_dir}'")
        if archive_originals and archive_dir:
            os.makedirs(archive_dir, exist_ok=True)
            print(f"Archive directory: '{archive_dir}'")
        
    # 5. Process and map files
    mapping_records = []
    print("\n" + "=" * 80)
    print(f"{'#':<4} | {'Timestamp':<10} | {'Original File':<38} | {'New Filename'}")
    print("=" * 80)
    
    for idx, (orig_path, (ts_raw, prompt_text)) in enumerate(zip(image_files, valid_prompts)):
        ts_clean = ts_raw.strip("[]").replace(":", "-")
        prefix = f"[{ts_clean}] "
        
        orig_name = os.path.basename(orig_path)
        stat = os.stat(orig_path)
        download_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        new_filename = sanitize_filename(prompt_text, prefix, ext=".jpg")
        dest_path = os.path.join(output_dir, new_filename)
        
        archived_location = ""
        if archive_originals and archive_dir:
            archived_location = os.path.join(archive_folder_name, orig_name)

        mapping_records.append({
            "index": idx + 1,
            "timestamp": ts_raw,
            "timestamp_clean": ts_clean,
            "download_time": download_time,
            "original_filename": orig_name,
            "new_filename": new_filename,
            "prompt_text": prompt_text,
            "archived_location": archived_location
        })
        
        short_orig = orig_name if len(orig_name) <= 36 else orig_name[:33] + "..."
        short_new = new_filename if len(new_filename) <= 45 else new_filename[:42] + "..."
        print(f"{idx+1:<4} | {ts_raw:<10} | {short_orig:<38} | {short_new}")
        
        if not dry_run:
            if action == "move":
                shutil.move(orig_path, dest_path)
            else:
                shutil.copy2(orig_path, dest_path)
                if archive_originals and archive_dir:
                    shutil.move(orig_path, os.path.join(archive_dir, orig_name))
                
    print("=" * 80)
    
    # 6. Save audit log / manifest
    if not dry_run:
        csv_path = os.path.join(output_dir, "mapping_manifest.csv")
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "index", "timestamp", "timestamp_clean", "download_time",
                "original_filename", "new_filename", "prompt_text", "archived_location"
            ])
            writer.writeheader()
            writer.writerows(mapping_records)
            
        json_path = os.path.join(output_dir, "mapping_manifest.json")
        with open(json_path, mode="w", encoding="utf-8") as f:
            json.dump(mapping_records, f, indent=2, ensure_ascii=False)
            
        print(f"\nSuccessfully processed {len(mapping_records)} images via '{action}'.")
        if archive_originals and archive_dir:
            print(f"All original images moved to dedicated archive: '{archive_dir}'")
            print("Main folder is now clean to welcome new images!")
        print(f"Manifest written to:\n - {csv_path}\n - {json_path}")
    else:
        print(f"\n[DRY RUN] Completed simulation for {len(mapping_records)} images.")
        
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize and rename downloaded images sequentially by prompt timestamps.")
    parser.add_argument("--dir", default=".", help="Source directory containing the images (default: current directory)")
    parser.add_argument("--output", default="organized_images", help="Subfolder name to store organized images (default: 'organized_images')")
    parser.add_argument("--action", choices=["copy", "move"], default="copy", help="Whether to copy or move files (default: copy)")
    parser.add_argument("--archive", default="original_images", help="Dedicated folder name to archive originals into (default: 'original_images')")
    parser.add_argument("--no-archive", action="store_true", help="Do not move originals to archive folder")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without copying or moving files")
    
    args = parser.parse_args()
    source_directory = os.path.abspath(args.dir)
    
    organize_images(
        source_dir=source_directory,
        output_folder_name=args.output,
        action=args.action,
        archive_originals=(not args.no_archive),
        archive_folder_name=args.archive,
        dry_run=args.dry_run
    )
