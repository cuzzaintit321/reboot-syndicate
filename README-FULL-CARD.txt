REBOOT SYNDICATE — FULL-CARD HOVER PHOTOS

All 14 images have had their blurred top and bottom padding cropped away.
Images are 900 x 506 px WebP in app/static/images/, matching the existing CSS.

On the server:
  cd ~/circuit-syndicate
  python3 -m zipfile -e reboot_syndicate_full_card_images.zip .
  git pull --ff-only origin main
  docker compose up -d --build website

This ZIP changes ONLY image assets, not app data, templates, CSS, or configuration.
The CSS update and expanded service detail pages are committed to GitHub.
