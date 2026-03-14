The Full Fortnite Experience:

| *>  Fort Grub <* | [Plymouth Loading Menu]**TODO**
| --- | ---  |

# Fort Grub 

A GRUB theme inspired by Fortnite.

![fort grub preview](preview/grub-preview.gif)

# Installation

- Clone or download the theme repository:

```bash
git clone https://github.com/PedroMMarinho/fortgrub-theme.git
```

## Manually

This theme will only have manual instalation:

Before you proceed, go to the [Fort Grub Wiki](https://github.com/PedroMMarinho/fortgrub-theme/wiki) to understand how to configure and generate the theme!

After that you can:

- **Check your GRUB directory:**
   - Usually one of:
     - `/boot/grub`
     - `/boot/grub2`

- **Copy the theme to GRUB themes directory**
   ```bash
   cd fortgrub-theme/
   sudo cp -r ./fortgrub $(GRUB_DIR)/themes/
    ```

- **Edit GRUB configuration**
  - Open `/etc/default/grub` with a text editor and add or modify the line:
  
       ```
       GRUB_THEME="/boot/grub/themes/fortgrub/theme.txt"
    ```

- **Update your grub config by running** 
  ```bash
  sudo grub-mkconfig -o /boot/grub/grub.cfg
    ```

- Finally, you need to update the classes of each boot entry and map them with their corresponding `id`.
  - There are two ways of doing this:
    - **Permanent**: You must use custom boot entry files. Add to each entry class its `id` (check inside `config.json`, e.g fortgrubX with X -> Number).
    - **Non-Permanent**: Add directly to `grub.cfg` the needed `id`. If you run `sudo grub-mkconfig -o /boot/grub/grub.cfg`, next time your classes for each entry will be gone.
  - I advise doing this manually, but you can also run `make map` to insert the classes for you.


For more info about custom entries checkout "wiki link TODO"

- And that's it. You are good to go.


## Improvements

Banner borders for different level threshold are missing. The code logic holds for different level borders but currently just have the base one located in `/assets/banners/borders`. If you'd like to contribute, you can create more `banner_border_X.png`, from the psd `banner_border.psd`, located in `assets/psds`.
For reference there is a video of all different borders in `assets/videos`.