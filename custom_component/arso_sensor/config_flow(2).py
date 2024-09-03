import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, LOCATIONS_URL

class ArsoWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for ARSO Weather."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input["location"], data=user_input)

        locations = await self._fetch_locations()

        schema = vol.Schema({
            vol.Required("location"): vol.In(locations)
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def _fetch_locations(self):
        """Fetch the list of locations from the external JSON."""
        async with aiohttp.ClientSession() as session:
            async with session.get(LOCATIONS_URL) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        # Izluščimo 'title' iz vsakega elementa v 'features'
                        locations = [item['properties']['title'] for item in data['features']]
                        return locations if locations else ["No locations found"]
                    except ValueError:
                        # Handle case where JSON decoding fails
                        return ["Error decoding JSON"]
                else:
                    # Return an error message if the status code is not 200
                    return [f"Error: Received status code {response.status}"]
