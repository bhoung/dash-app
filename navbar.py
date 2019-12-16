import dash_bootstrap_components as dbc

def Navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Harvest by Tile", href="/harvest-tile")),
            dbc.NavItem(dbc.NavLink("Aggregate Harvest", href="/aggregate-harvest")),
          ],
          brand="Satellite Datathon",
          brand_href="/home",
          sticky="top",
        )
    return navbar