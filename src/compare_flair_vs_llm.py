# from ner_in_docker.use_cases.GetFlairEntitiesUseCase import GetFlairEntitiesUseCase
from ner_in_docker.use_cases.GetLLMEntitiesUseCase import GetLLMEntitiesUseCase

if __name__ == "__main__":
    sample_texts = [
        "Barack Obama was born in Hawaii and served as the 44th President of the United States.",
        "The United Nations headquarters is located in New York City and was established in 1945.",
        "Apple Inc. and Microsoft Corporation are competing in the technology sector.",
        "The Civil Rights Act was signed into law by President Lyndon B. Johnson in Washington, D.C.",
        "Dr. Maria Rodriguez-Garcia, CEO of TechVision AI, announced the merger with Beijing-based Quantum Computing Ltd. at the World Economic Forum in Davos, Switzerland.",
        "The European Central Bank (ECB) and the Federal Reserve (Fed) coordinated their response to the 2008 financial crisis alongside the International Monetary Fund.",
        "In 1969, NASA's Apollo 11 mission, commanded by Neil Armstrong, landed on the Moon, while the Soviet Union's Luna program continued unmanned exploration.",
        "Stanford University professor Andrew Ng founded Google Brain and later became Chief Scientist at Baidu before launching deeplearning.ai and Coursera.",
        "The Treaty of Versailles, signed on June 28, 1919, at the Palace of Versailles near Paris, officially ended World War I between Germany and the Allied Powers.",
        "J.P. Morgan Chase & Co. acquired Bear Stearns for $10 per share in March 2008, facilitated by the U.S. Treasury and the Federal Reserve Bank of New York.",
        "Marie Curie, born Maria Sklodowska in Warsaw, Poland, won Nobel Prizes in Physics (1903) and Chemistry (1911) for her research on radioactivity.",
        "The WHO declared COVID-19 a pandemic on March 11, 2020, after the virus spread from Wuhan, China to over 114 countries worldwide.",
        "Amazon Web Services (AWS), launched by Jeff Bezos's Amazon.com in 2006, competes with Microsoft Azure and Google Cloud Platform in the cloud computing market.",
        "The Battle of Waterloo on June 18, 1815, saw the Duke of Wellington and Gebhard Leberecht von Blücher defeat Napoleon Bonaparte, ending the Napoleonic Wars.",
        "OpenAI's ChatGPT, released in November 2022 by Sam Altman's company, sparked a race with Google's Bard and Anthropic's Claude in generative AI technology.",
        "Dr. A.P.J. Abdul Kalam, India's 'Missile Man', worked with ISRO and DRDO before becoming President, while his colleague Dr. V.S. Arunachalam headed the Defence Research and Development Organisation.",
        "The SEC charged Goldman Sachs Group Inc., Morgan Stanley, and J.P. Morgan with violations related to WhatsApp communications, resulting in fines totaling $1.8B.",
        "Xi Jinping met with Vladimir Putin at the Belt and Road Initiative (BRI) summit in Beijing to discuss the China-Russia Energy Agreement and Nord Stream 2 pipeline project.",
        "Prof. Yoshua Bengio (Université de Montréal), Geoffrey Hinton (Google/University of Toronto), and Yann LeCun (Meta/NYU) won the 2018 Turing Award for deep learning breakthroughs.",
        "The FDA approved Pfizer-BioNTech's Comirnaty and Moderna's Spikevax vaccines after Phase III clinical trials conducted at Johns Hopkins University and Massachusetts General Hospital.",
        "Justice Ruth Bader Ginsburg, nominated by President Bill Clinton in 1993, served on the U.S. Supreme Court alongside Justices Sonia Sotomayor and Elena Kagan.",
        "Elon Musk's Tesla, Inc. opened Gigafactory Berlin-Brandenburg in Grünheide, Germany, while SpaceX's Starbase facility in Boca Chica, Texas launched Starship prototypes.",
        "The IMF, World Bank, and WTO held joint meetings in Geneva, Switzerland with ECB President Christine Lagarde and Fed Chair Jerome Powell to address inflation.",
        "In the trial USA v. Elizabeth Holmes, the Theranos CEO was convicted of fraud in San Jose, California, with testimony from former Secretary of State George Shultz's grandson.",
        "Crown Prince Mohammed bin Salman (MBS) launched Saudi Vision 2030 and NEOM megacity project, partnering with SoftBank's Masayoshi Son on a $500B investment.",
        "The IPCC report, co-authored by scientists from MIT, Caltech, and the Max Planck Institute, warned of 1.5°C warming by 2030 under RCP8.5 scenarios.",
        "Manchester United F.C. signed Cristiano Ronaldo from Juventus F.C. for €15M, reuniting him with coach Ole Gunnar Solskjær at Old Trafford.",
        "Rep. Alexandria Ocasio-Cortez (D-NY) and Sen. Bernie Sanders (I-VT) introduced the Green New Deal resolution in Congress, endorsed by Sunrise Movement activists.",
        "The U.S. v. Google antitrust case, filed by DOJ's Antitrust Division under AG Merrick Garland, focuses on Google Search's dominance over Bing and DuckDuckGo.",
        "Ambassador Nikki Haley resigned from her position as U.S. Representative to the UN, where she worked with Secretary-General António Guterres on North Korea sanctions.",
        "The People's Bank of China (PBOC) Governor Yi Gang coordinated with Bank of Japan (BOJ) Governor Haruhiko Kuroda on forex intervention to stabilize CNY/JPY exchange rates.",
        "Meta Platforms Inc. (formerly Facebook, Inc.) CEO Mark Zuckerberg announced layoffs affecting Reality Labs, Instagram, and WhatsApp divisions at the Menlo Park headquarters.",
        "Special Counsel Robert Mueller's investigation into Russian interference featured testimony from Michael Flynn, Paul Manafort, and Roger Stone before Judge Amy Berman Jackson.",
        "The 2022 FIFA World Cup in Qatar saw Argentina's Lionel Messi defeat France's Kylian Mbappé at Lusail Stadium, with FIFA President Gianni Infantino presenting the trophy.",
        "NATO Secretary General Jens Stoltenberg met with Ukrainian President Volodymyr Zelenskyy and Polish President Andrzej Duda at the Ramstein Air Base summit in Germany.",
    ]

    # print("=" * 80)
    # print("COMPARING FLAIR vs LLM ENTITY EXTRACTION")
    # print("=" * 80)
    #
    flair_results = {}
    llm_results = {}
    #
    # print("\n" + "=" * 80)
    # print("PHASE 1: Running FLAIR Extraction")
    # print("=" * 80)
    #
    # flair_extractor = GetFlairEntitiesUseCase()
    #
    # for i, text in enumerate(sample_texts, 1):
    #     print(f"\n[FLAIR - TEST {i}]: {text}")
    #     flair_entities = flair_extractor.get_entities(text)
    #     flair_results[i] = (text, flair_entities)
    #     if flair_entities:
    #         for entity in flair_entities:
    #             print(f"  - {entity.text:30} | {entity.type:15} | Pos: {entity.character_start}-{entity.character_end}")
    #     else:
    #         print("  No entities found")
    #     print(f"  Total: {len(flair_entities)} entities")
    #
    # del flair_extractor

    print("\n" + "=" * 80)
    print("PHASE 2: Running LLM Extraction")
    print("=" * 80)

    llm_extractor = GetLLMEntitiesUseCase()
    print(f"\nLLM Model: {llm_extractor.model_name}")
    print(f"LLM Host: {llm_extractor.host}\n")

    for i, text in enumerate(sample_texts, 1):
        print(f"\n[LLM - TEST {i}]: {text}")
        try:
            llm_entities = llm_extractor.get_entities(text)
            llm_results[i] = (text, llm_entities)
            if llm_entities:
                for entity in llm_entities:
                    print(f"  - {entity.text:30} | {entity.type:15} | Pos: {entity.character_start}-{entity.character_end}")
            else:
                print("  No entities found")
            print(f"  Total: {len(llm_entities)} entities")
        except Exception as e:
            print(f"  Error: {e}")
            llm_results[i] = (text, [])

    del llm_extractor

    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)

    for i in range(1, len(sample_texts) + 1):
        text, flair_entities = flair_results[i]
        _, llm_entities = llm_results[i]
        print(f"\nTEST {i}: {text}")
        print(f"  Flair: {len(flair_entities)} entities | LLM: {len(llm_entities)} entities")

    print("\n" + "=" * 80)
    print("COMPARISON COMPLETE")
    print("=" * 80)
