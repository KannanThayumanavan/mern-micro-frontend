const { ModuleFederationPlugin } = require("webpack").container;
const path = require("path");
module.exports = {
  entry: "./index.js",
  mode: "development",
  devtool: "hidden-source-map",
  output: {
    publicPath: "http://localhost:3001/",
    clean: true,
  },
  module: {},
  plugins: [
    new ModuleFederationPlugin({
      name: "mangahigh_libs",
      filename: "remoteEntry.js",
      exposes: {
        "./react": "react",
        "./react-dom": "react-dom",
        "./react-router-dom": "react-router-dom",
      },
    }),
  ],
};
