let auth0 = null;
let endpoint = null



const fetchAuthConfig = () => fetch("/auth_config.json");


const configureClient = async () => {
  const response = await fetchAuthConfig();
  const config = await response.json();

  auth0 = await createAuth0Client({
    domain: config.domain,
    client_id: config.clientId,
    audience: config.audience,
  });

  endpoint = config.api_endpoint
};



window.onload = async () => {
  // Configure the Auth0 Client
  await configureClient();

  updateUI();


  //check for the code and state parameters.. These are set when redirected back from Auth0 universal login page
  const query = window.location.search;
  if (query.includes("code=") && query.includes("state=")) {

    // Process the login state
    await auth0.handleRedirectCallback();

    updateUI();

    // Use replaceState to redirect the user away and remove the querystring parameters
    window.history.replaceState({}, document.title, "/");
  }
};


const updateUI = async () => {

  const isAuthenticated = await auth0.isAuthenticated();

  // Update button states
  document.getElementById("btn-logout").disabled = !isAuthenticated;
  document.getElementById("btn-api").disabled = !isAuthenticated;
  document.getElementById("btn-login").disabled = isAuthenticated;

  if (isAuthenticated) {
    // If the user is authenticated, display the authentication token and user settings from Auth0
    document.getElementById("gated-content").classList.remove("hidden");
    document.getElementById("welcome-content").classList.add("hidden");

    document.getElementById(
      "ipt-access-token"
    ).innerHTML = await auth0.getTokenSilently();

    document.getElementById("ipt-user-profile").textContent = JSON.stringify(
      await auth0.getUser()
    );

  } else {
    document.getElementById("gated-content").classList.add("hidden");
    document.getElementById("welcome-content").classList.remove("hidden");
  }
};

/*
Login and Logout
*/

const login = async () => {
  // redirect to the Auth0 Universal login page
  await auth0.loginWithRedirect({
    redirect_uri: window.location.origin
  });
};

const logout = () => {
  auth0.logout({
    returnTo: window.location.origin
  });
};


function formatParams( params ){
  return "?" + Object
        .keys(params)
        .map(function(key){
          return key+"="+encodeURIComponent(params[key])
        })
        .join("&")
}

const hit_api = async () => {
  const isAuthenticated = await auth0.isAuthenticated();

  if (isAuthenticated){
    access_token = await auth0.getTokenSilently();
    user = await auth0.getUser()

    var params = {
      user_id: user.sub,
    }

    var final_endpoint = endpoint + "/demo" + formatParams(params)
    fetch(final_endpoint,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + access_token
        }
      }
    )
    .then(response => response.json())
    .then(
      data => {
        rv = JSON.parse(data.body)
        alert(rv.message)

      });


  }

  else {
    alert("You need to be logged in")
  }
}
