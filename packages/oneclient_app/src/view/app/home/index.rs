use freya::prelude::*;

use crate::components::{ActiveClusterPanel, RecentsRow};
use crate::theme;

#[derive(PartialEq)]
pub struct Home;

impl Component for Home {
    fn render(&self) -> impl IntoElement {
        rect()
            .vertical()
            .width(Size::fill())
            .height(Size::fill())
            .content(Content::Flex)
            .overflow(Overflow::Clip)
            .padding(theme::HOME_PADDING_PX)
            .main_align(Alignment::Center)
            .child(
                rect()
                    .vertical()
                    .width(Size::fill())
                    .spacing(8.)
                    .padding(Gaps::new(8., 0., 24., 0.))
                    .child(
                        label()
                            .text("NOVEX CLIENT")
                            .font_size(text_size(13.))
                            .font_weight(FontWeight::BOLD)
                            .color(theme::colors::brand()),
                    )
                    .child(
                        label()
                            .text("Your Minecraft. Your way.")
                            .font_size(text_size(25.))
                            .font_weight(FontWeight::BOLD)
                            .color(theme::colors::on_art()),
                    )
                    .child(
                        label()
                            .text("Launch your instances, manage your mods, and get straight into the game.")
                            .font_size(text_size(13.))
                            .color(theme::colors::on_art_secondary()),
                    ),
            )
            .child(
                rect()
                    .vertical()
                    .width(Size::fill())
                    .height(Size::flex(1.0))
                    .main_align(Alignment::Center)
                    .child(ActiveClusterPanel),
            )
            .child(RecentsRow)
    }
}
