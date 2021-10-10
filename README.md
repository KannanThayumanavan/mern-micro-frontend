# mern-micro-frontend
#### Mangahigh Tech Assignment Micro Frontend Full stack app, build with

  MERN stack (MongoDB Express React Node) - https://www.mongodb.com/mern-stack
  
  Webpack Module Federation Micro-Frontend - https://webpack.js.org/concepts/module-federation/

## Installation
  ### server - to start Express NodeJS server and connect with mongoDB
     
     cd server
     
     npm install
     
     npm install -g nodemon
     
     nodemon server
     
  ### client - to run all independent modules as a single app
     
     cd client
    
     npm install
    
     npx lerna bootstrap
    
     npm run start
     
## Run modules independently
  ### mangahigh-libs - required to run other modules
  
  It is a low-level or basic app, which exposes libraries like react, react-dom.
  
  It is a pure remote
  
    cd client 
    cd mangahigh-libs
    npm start    
    
  Navigate to http://localhost:3001 in browser to see all exposed bundles.
    
  ### mangahigh-components - dependency, contains all re-usable components.
  
  It is a middle-level app, which depends on modules exposed from mangahigh-libs : react ,react-dom. In the meantime, it also exposes components: Button, DisplayCard to other apps (mangahigh-insights-module, mangahigh-quiz-module).

  It is both host and remote.
  
    cd client 
    cd mangahigh-components
    npm start
  
  Navigate to http://localhost:3002 in browser to see all available re-usable components
  
  ### mangahigh-insights-module - independent module for insights page
  
  It is a middle-level app, which depends on modules exposed from mangahigh-libs. It is both host and remote.
  
    cd client 
    cd mangahigh-insights-module
    npm start
  
  Navigate to http://localhost:3003 in browser to see insights module running independently, and data fetched from MongoDB
  
  ### mangahigh-quiz-module - independent module for Quiz page
  
  It is a middle-level app, which depends on modules exposed from mangahigh-libs. It is both host and remote.
  
    cd client 
    cd mangahigh-insights-module
    npm start
    
  Navigate to http://localhost:3004 in browser to see quiz module running independently, and data fetched, posted to MongoDB
    
  ### mangahigh-root-container

  The top-level app, which depends on all the above modules.

  It is a pure host.
      
  ### Run test and eslint 
    (mangahigh-componets, mangahigh-insights-module, mangahigh-quiz-module)
  
    cd <module-name>
    npm run test
    npm run lint
    
 ## Questions from assignment
  ### How you approached the project
  
   Read the document 
   
   Decided to go with the micro-frontend architectural approach
   
   Bootstrap(styles only) for responsive design
   
   Separated the features into independent modules, one to implement micro-frontend and another to improve the developer experience
   
   Must be unit tested

  ### What aspects of your solution you’re most happy with
  
   MERN and Webpack Federation
    
  ### What you would do differently or improve on, given more time
  
   i18n Support
    
   Error boundary, SSR, CSS modules
    
   Jest browser snapshot testing
    
   Webpack independent test build based unit testing - https://scriptedalchemy.medium.com/module-federation-how-do-we-create-unit-tests-for-it-bd0d73c999bc
    
   eslint with full config (only syntax check included now)
    
   Encryption and decryption of data (stored in MongoDB)
    
  ### Roughly how long spent in total
  
   6 - 8 hours, that also includes a bit of learning, machine setup
    
    
    
    
    
    
     
  
