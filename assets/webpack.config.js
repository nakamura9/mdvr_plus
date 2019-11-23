var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

module.exports = {
  context: __dirname,

  entry: {
      base: './js/index',
      calendar: './js/calendar/calendar',
      dashboard: './js/dashboard/dashboard',
      reminder: './js/reminders/reminder'
    }, 
  output: {
      path: path.resolve('./bundles/'),
      filename: "[name].js",
  },
  mode: 'development',

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
  ],

  module: {
        rules: [
            {
                test: /\.css$/,
                'loader': 'style-loader'
            },
            {
                test: /\.css$/,
                loader: 'css-loader',
                query: {
                    modules: {
                        localIdentName: '[name]__[local]__[hash:64:5]'
                    },
                    
                }
            },
            {
                test: /\.js$/,
                loader: 'babel-loader',
                exclude: /node_modules/,
                query: {
                    presets: ['stage-2','react']//stage 2 for class level attrs and autobind
                }
            }

        ]
  },

  resolve: {
    extensions: [ '.js', '.jsx']
  },
}
