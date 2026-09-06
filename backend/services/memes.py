import random  # picks one meme per request

# Memes are rendered by memegen.link: the caption is encoded in the URL
# itself (underscores become spaces), so there's no image to host and no API
# key. Each entry is hand-tagged with a topic, which is what a vote on this
# section records.
#
# `id` is the vote `item` — a stable slug, so rewording a joke doesn't turn
# it into a different meme in the votes table.
MEMES = [
    {
        "id": "panik-healthy-correction",
        "imageUrl": "https://api.memegen.link/images/panik-kalm-panik/Bitcoin_drops_10_percent/Just_a_healthy_correction/Bitcoin_drops_30_percent.png",
        "alt": "Panik Kalm Panik meme about calling a 10 percent drop healthy, then it drops 30 percent",
        "topic": "BTC",
    },
    {
        "id": "galaxy-brain-seed-phrase",
        "imageUrl": "https://api.memegen.link/images/gb/Buy_high_sell_low/Buy_low_sell_high/Just_hold_forever/Lose_the_seed_phrase.png",
        "alt": "Galaxy Brain meme ending with losing the seed phrase as the ultimate strategy",
        "topic": "BTC",
    },
    {
        "id": "success-kid-remembers-password",
        "imageUrl": "https://api.memegen.link/images/success/Bought_bitcoin_in_2013/Still_remembers_the_password.png",
        "alt": "Success Kid meme about buying bitcoin in 2013 and still remembering the password",
        "topic": "BTC",
    },
    {
        "id": "drake-gas-timing",
        "imageUrl": "https://api.memegen.link/images/drake/Paying_80_dollars_in_gas/Setting_an_alarm_for_4am_Sunday.png",
        "alt": "Drake rejecting an 80 dollar gas fee, approving waking at 4am for cheaper fees",
        "topic": "ETH",
    },
    {
        "id": "woman-cat-doge-zero",
        "imageUrl": "https://api.memegen.link/images/woman-cat/It_is_going_to_zero/Doge_holder_since_2013.png",
        "alt": "Woman yelling at a cat, with the cat as a Dogecoin holder since 2013",
        "topic": "DOGE",
    },
    {
        "id": "success-kid-doge-rent",
        "imageUrl": "https://api.memegen.link/images/success/Bought_dogecoin_as_a_joke/The_joke_paid_my_rent.png",
        "alt": "Success Kid meme about buying Dogecoin as a joke that ended up paying rent",
        "topic": "DOGE",
    },
    {
        "id": "fine-solana-halt",
        "imageUrl": "https://api.memegen.link/images/fine/The_network_halted_again/This_is_fine.png",
        "alt": "This Is Fine dog sitting in flames after the network halted again",
        "topic": "SOL",
    },
    {
        "id": "grumpycat-xrp-sold",
        "imageUrl": "https://api.memegen.link/images/grumpycat/XRP_finally_pumped/I_sold_last_week.png",
        "alt": "Grumpy Cat unimpressed that XRP pumped the week after selling",
        "topic": "XRP",
    },
    {
        "id": "disastergirl-xrp-breakeven",
        "imageUrl": "https://api.memegen.link/images/disastergirl/Waited_seven_years_for_this_pump/Sold_at_breakeven.png",
        "alt": "Disaster Girl smirking after waiting seven years for a pump and selling at breakeven",
        "topic": "XRP",
    },
    {
        "id": "gru-buy-the-dip",
        "imageUrl": "https://api.memegen.link/images/gru/Buy_the_dip/Wait_for_the_bounce/Dip_keeps_dipping/Dip_keeps_dipping.png",
        "alt": "Gru's Plan meme where buying the dip ends with the dip continuing to dip",
        "topic": "general",
    },
    {
        "id": "stonks-sold-the-bottom",
        "imageUrl": "https://api.memegen.link/images/stonks/Sold_at_the_bottom/Bought_back_20_percent_higher.png",
        "alt": "Stonks meme about selling at the bottom and buying back 20 percent higher",
        "topic": "general",
    },
    {
        "id": "harold-family-dinner",
        "imageUrl": "https://api.memegen.link/images/harold/Explaining_crypto_at_family_dinner/Nobody_asks_a_second_question.png",
        "alt": "Hide the Pain Harold smiling after explaining crypto at dinner to no follow up questions",
        "topic": "general",
    },
    {
        "id": "stonks-exchange-own-token",
        "imageUrl": "https://api.memegen.link/images/stonks/Exchange_launches_its_own_chain/Exchange_lists_its_own_token.png",
        "alt": "Stonks meme about an exchange launching a chain and listing its own token",
        "topic": "BNB",
    },
    {
        "id": "harold-litecoin-ignored",
        "imageUrl": "https://api.memegen.link/images/harold/Litecoin_has_worked_for_13_years/Nobody_talks_about_it.png",
        "alt": "Hide the Pain Harold smiling because Litecoin works but nobody discusses it",
        "topic": "LTC",
    },
    {
        "id": "spiderman-polygon-rebrand",
        "imageUrl": "https://api.memegen.link/images/spiderman/Polygon/Polygon_after_the_rebrand.png",
        "alt": "Two Spider-Men pointing at each other, labelled Polygon and Polygon after the rebrand",
        "topic": "MATIC",
    },
    {
        "id": "same-doge-shib",
        "imageUrl": "https://api.memegen.link/images/same/Dogecoin/Shiba_Inu/They_are_the_same_picture.png",
        "alt": "The Office meme calling Dogecoin and Shiba Inu the same picture",
        "topic": "SHIB",
    },
    {
        "id": "blb-billion-supply",
        "imageUrl": "https://api.memegen.link/images/blb/Buys_a_coin_with_a_quadrillion_supply/Waits_for_it_to_reach_one_dollar.png",
        "alt": "Bad Luck Brian waiting for a coin with enormous supply to reach one dollar",
        "topic": "SHIB",
    },
    {
        "id": "toohigh-fees",
        "imageUrl": "https://api.memegen.link/images/toohigh/The_transaction_fee/Is_too_damn_high.png",
        "alt": "The Rent Is Too Damn High man complaining the transaction fee is too high",
        "topic": "BTC",
    },
    {
        "id": "whatyear-still-a-bubble",
        "imageUrl": "https://api.memegen.link/images/whatyear/Woke_up_from_a_four_year_nap/Bitcoin_is_still_called_a_bubble.png",
        "alt": "What Year Is It meme about Bitcoin still being called a bubble",
        "topic": "BTC",
    },
    {
        "id": "ds-stake-or-liquid",
        "imageUrl": "https://api.memegen.link/images/ds/Stake_my_ETH/Keep_it_liquid/Difficult_choice.png",
        "alt": "Daily Struggle meme choosing between staking ETH and keeping it liquid",
        "topic": "ETH",
    },
    {
        "id": "midwit-just-buy-eth",
        "imageUrl": "https://api.memegen.link/images/midwit/Just_buy_ETH/Rotate_into_L2_tokens_with_better_risk_adjusted_returns/Just_buy_ETH.png",
        "alt": "Midwit meme where both ends conclude to simply buy ETH",
        "topic": "ETH",
    },
    {
        "id": "kombucha-tokenomics",
        "imageUrl": "https://api.memegen.link/images/kombucha/Reading_the_tokenomics/Buying_anyway.png",
        "alt": "Kombucha Girl reacting badly to tokenomics then buying anyway",
        "topic": "general",
    },
    {
        "id": "sadfrog-green-portfolio",
        "imageUrl": "https://api.memegen.link/images/sadfrog/Portfolio_finally_green/Only_because_I_added_more_money.png",
        "alt": "Feels Bad Man whose portfolio is green only from adding more money",
        "topic": "general",
    },
    {
        "id": "red-down-before-coffee",
        "imageUrl": "https://api.memegen.link/images/red/Market_opens/Down_8_percent_before_coffee.png",
        "alt": "Oh Is That What We Are Doing Today meme about the market dropping before coffee",
        "topic": "general",
    },
    {
        "id": "wkh-trust-crypto",
        "imageUrl": "https://api.memegen.link/images/wkh/Why_does_nobody_trust_crypto/Another_exchange_collapses/Why_does_nobody_trust_crypto.png",
        "alt": "Who Killed Hannibal meme asking why nobody trusts crypto after an exchange collapse",
        "topic": "general",
    },
    {
        "id": "elf-guaranteed-apy",
        "imageUrl": "https://api.memegen.link/images/elf/Guaranteed_20_percent_APY/You_sit_on_a_throne_of_lies.png",
        "alt": "Buddy the Elf calling a guaranteed 20 percent APY a throne of lies",
        "topic": "general",
    },
    {
        "id": "gone-life-savings",
        "imageUrl": "https://api.memegen.link/images/gone/My_life_savings/And_it_is_gone.png",
        "alt": "South Park bank teller meme about life savings disappearing instantly",
        "topic": "general",
    },
    {
        "id": "regret-all-in-top",
        "imageUrl": "https://api.memegen.link/images/regret/Went_all_in_at_the_top/I_immediately_regret_this_decision.png",
        "alt": "Anchorman meme about going all in at the top and immediately regretting it",
        "topic": "general",
    },
    {
        "id": "worst-dip-so-far",
        "imageUrl": "https://api.memegen.link/images/worst/This_is_the_worst_dip_ever/So_far.png",
        "alt": "The Worst Day Of Your Life So Far meme about the worst dip so far",
        "topic": "general",
    },
    {
        "id": "cryingfloor-opened-portfolio",
        "imageUrl": "https://api.memegen.link/images/cryingfloor/Opened_my_portfolio/Closed_it_immediately.png",
        "alt": "Person crying on the floor after opening and immediately closing their portfolio",
        "topic": "general",
    },
    {
        "id": "facepalm-sold-at-a-loss",
        "imageUrl": "https://api.memegen.link/images/facepalm/Sold_at_a_loss/It_doubled_the_next_day.png",
        "alt": "Picard facepalm after selling at a loss and watching it double the next day",
        "topic": "general",
    },
    {
        "id": "crazypills-still-early",
        "imageUrl": "https://api.memegen.link/images/crazypills/Everyone_says_we_are_still_early/We_are_down_80_percent.png",
        "alt": "Taking Crazy Pills meme about being told it is early while down 80 percent",
        "topic": "general",
    },
    {
        "id": "hagrid-safe-investment",
        "imageUrl": "https://api.memegen.link/images/hagrid/Told_my_wife_it_was_a_safe_investment/I_should_not_have_said_that.png",
        "alt": "Hagrid regretting telling his wife it was a safe investment",
        "topic": "general",
    },
    {
        "id": "chosen-supposed-to-go-up",
        "imageUrl": "https://api.memegen.link/images/chosen/You_were_supposed_to_go_up/Not_down_90_percent.png",
        "alt": "Obi-Wan shouting that it was supposed to go up, not down 90 percent",
        "topic": "general",
    },
    {
        "id": "oprah-everybody-gets-a-loss",
        "imageUrl": "https://api.memegen.link/images/oprah/You_get_a_loss/Everybody_gets_a_loss.png",
        "alt": "Oprah giving everyone in the audience a loss",
        "topic": "general",
    },
    {
        "id": "tenguy-one-more-trade",
        "imageUrl": "https://api.memegen.link/images/tenguy/Bro_just_one_more_leveraged_trade/It_will_fix_everything.png",
        "alt": "10 Guy insisting one more leveraged trade will fix everything",
        "topic": "general",
    },
]


# a fresh random meme on every call — deliberately not cached, unlike the
# other three sections, since the meme is meant to change on every page load
def get_meme():
    return random.choice(MEMES)
