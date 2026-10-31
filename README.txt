REBOOT SYNDICATE — 14 FULL-HEIGHT HOVER PHOTOS

The old card images have been replaced with 1200 x 740 full-bleed WebP assets.
The installer also prevents any existing short image strip from showing.
It leaves all page content, prices, forms, backend data, Caddy and Pi-hole alone.

On Fedora:
  scp ~/Downloads/reboot_full_height_hover_fix.zip yeet:~/circuit-syndicate/
On yeet:
  cd ~/circuit-syndicate
  python3 -m zipfile -e reboot_full_height_hover_fix.zip .
  python3 install_full_height_images.py
  docker compose up -d --build website
Then refresh with Ctrl+Shift+R.

Original files are saved under backups/full-height-hover-<timestamp>.
