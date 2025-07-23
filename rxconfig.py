import reflex as rx
from llm_hugo_course.style import create_colors_dict

tailwind_config={
    "darkMode": "class",   
    "theme": {
        "colors": {
            **create_colors_dict(),
        },
    },
}

config = rx.Config(
    app_name="llm_hugo_course",    
    # api_url="http://localhost:9000",    
    backend_port=9000,
    # deployment_name="deployment",    
    # plugins=[rx.plugins.TailwindV3Plugin()],    
    # # tailwind=None,
    plugins=[
        rx.plugins.TailwindV3Plugin(tailwind_config),
        rx.plugins.sitemap.SitemapPlugin(),
    ],
)
 