import reflex as rx
from word_map.state import State

template_prompts_ddicts = {
    "jobs": {"icon": "route",
             "title": "Get all job positions",
             "description": "Make a list of all the people mentioned and their past and current places of employment. Your output should be a table with the people's first and last name as column titles, and each employment place as a cell under the respective names",
    },
    "countries": {"icon": "earth",
                  "title": "Map countries of employment",
                  "description": "Plot a world map and place a pin on each country where the people mentioned worked, with the pin label being the first and last names of the person in question",
    },
    "skills": {"icon": "brain-circuit",
               "title": "List skills",
               "description": "Make a table with every skill mentioned as the first cell in each row and the names of each person mentioned as the title of a different column. Then add a cross in every cell corresponding to the person and relevant skill. Make sure that the cross is centred horizontally in every column",
    },
    "languages": {"icon": "languages",
                  "title": "Show all languages",
                  "description": "For every person mentioned, write their first name, last name, and draw next to these the flags corresponding to every language they mention in their language skills",
    }
}

def template_card(icon: str, title: str, description: str, color: str) -> rx.Component:
    return rx.el.button(
        rx.icon(tag=icon, color=rx.color(color, 9), size=32),
        rx.text(title, class_name="font-medium text-slate-11 text-sm"),
        # rx.text(description, class_name="text-slate-10 text-xs"),
        class_name="relative align-top flex flex-col gap-2 border-slate-4 bg-slate-1 hover:bg-slate-3 shadow-sm px-3 pt-3 pb-4 border rounded-2xl text-[15px] text-start transition-colors",
        # on_click=lambda: State.ask_answer_question(description),
        on_click=[State.set_question(description), State.answer],
    )


def templates() -> rx.Component:
    return rx.box(
        rx.heading("Find Your Future Recruits (incl. Eval loop)"),
        rx.image(
            src="/word_map.png",
            height="200px",
            border_radius="150px 150px",
            # class_name="opacity-70 w-auto h-11 pointer-events-none",
        ),
        # rx.hstack(
        #    rx.text.kbd("Enter"),
        #    rx.text("the world of your documents", size="4")
        # ),
        rx.box(
            template_card(
                template_prompts_ddicts["jobs"]["icon"],
                template_prompts_ddicts["jobs"]["title"],
                template_prompts_ddicts["jobs"]["description"],
                "grass",
            ),
            template_card(
                template_prompts_ddicts["countries"]["icon"],
                template_prompts_ddicts["countries"]["title"],
                template_prompts_ddicts["countries"]["description"],
                "tomato",
            ),
            template_card(
                template_prompts_ddicts["skills"]["icon"],
                template_prompts_ddicts["skills"]["title"],
                template_prompts_ddicts["skills"]["description"],
                "blue",
            ),
            template_card(
                template_prompts_ddicts["languages"]["icon"],
                template_prompts_ddicts["languages"]["title"],
                template_prompts_ddicts["languages"]["description"],
                "blue",
            ),
            class_name="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 w-full",
        ),
        class_name="top-1/3 left-1/2 absolute flex flex-col justify-center items-center gap-10 w-full max-w-4xl transform -translate-x-1/2 -translate-y-1/2 px-6 z-50",
        style={
            "animation": "reveal 0.35s ease-out",
            "@keyframes reveal": {"0%": {"opacity": "0"}, "100%": {"opacity": "1"}},
        },
        display=rx.cond(State.chat_history, "none", "flex"),
    )
