
    const { TABS, TOOLS } = FilerobotImageEditor;

    document.getElementById('image_upload').addEventListener('change', function(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          const imageUrl = e.target.result;
          initializeEditor(imageUrl);
        };
        reader.readAsDataURL(file); // Read the file as a data URL
      }
    });

    function initializeEditor(imageUrl) {
      const config = {
        source: imageUrl, 
        closeAfterSave: true,
        onSave: (editedImageObject) =>{
          console.log(editedImageObject.imageBase64);
          var inputElement = document.getElementById("base64");
          inputElement.value = editedImageObject.imageBase64;
        },
        annotationsCommon: {
          fill: '#ff0000',
        },
        Text: { text: 'Put quote here...' },
        Rotate: { angle: 90, componentType: 'slider' },
        translations: {
          profile: 'Profile',
          coverPhoto: 'Cover photo',
          facebook: 'Facebook',
          socialMedia: 'Social Media',
          fbProfileSize: '180x180px',
          fbCoverPhotoSize: '820x312px',
        },
        Crop: {
          presetsItems: [
            {
              titleKey: 'classicTv',
              descriptionKey: '4:3',
              ratio: 4 / 3,
            },
            {
              titleKey: 'cinemascope',
              descriptionKey: '21:9',
              ratio: 21 / 9,
            },
          ],
          presetsFolders: [
            {
              titleKey: 'socialMedia',
              groups: [
                {
                  titleKey: 'facebook',
                  items: [
                    {
                      titleKey: 'profile',
                      width: 180,
                      height: 180,
                      descriptionKey: 'fbProfileSize',
                    },
                    {
                      titleKey: 'coverPhoto',
                      width: 820,
                      height: 312,
                      descriptionKey: 'fbCoverPhotoSize',
                    },
                  ],
                },
              ],
            },
          ],
        },
        tabsIds: [TABS.ADJUST, TABS.ANNOTATE, TABS.WATERMARK],
        defaultTabId: TABS.ANNOTATE,
        defaultToolId: TOOLS.TEXT,
      };

      const filerobotImageEditor = new FilerobotImageEditor(
        document.querySelector('#editor_container'),
        config,
      );

      filerobotImageEditor.render({
        onClose: (closingReason) => {
          console.log('Closing reason', closingReason);
          filerobotImageEditor.terminate();
        },
      });
    }