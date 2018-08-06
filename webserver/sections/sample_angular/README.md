This section is a configured to integrate Angular2JS as a Front-End FrameWork. The code from theBack-End (BottlePY) is kept separate from the Front-End.

All the Python classes of the OOP designed Bottle application are located in the main sections sub-module folder, while all the Angular2 code and required modules are located in the `js` folder.

The `package.json` file, providing npm settings, is located in the `js` folder, alongside the `node_modules` folder where node modules are installed. To install more node modules, go to the js folder and use `npm install packagename`. The `systemjs.config.js` file is also located in the js folder. The app files, implemented in TypeScript, are located in the `./js/app` folder. To compile them go to the `js` folder and run `tsc --watch`.

```

+ pool_design
  |
  + css
  + js
  | + app
  | | - appFiles.ts
  | + node_modules
  | | - npm installed modules
  | - package.json
  | - systemjs.config.js
  | - tsconfig.json
  |
  + views
  | - templates.tpl
  - app.py
  - routes.py
  - otherClasses.py

```