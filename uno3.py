import pygame
from UNONetwork import Network




def start_game(username, network):
    pygame.init()
    WIDTH,HEIGHT = 1280,720
    win=pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("UNO Multiplayer")
    clock=pygame.time.Clock()

    #network types thingy
    #net=Network()            no need cuz created duplicate connections
    player_id = None

    #card stuff
    CARD_W,CARD_H=110,165
    CARD_FOLDER="./assets/cards"                      ## CHANGED ROOT FOLDER

    CARD_IMAGES = {}

    def load_images():
        import os
        for f in os.listdir(CARD_FOLDER):
            if f.endswith(".png"):
                img = pygame.image.load(f"{CARD_FOLDER}/{f}").convert_alpha()
                img = pygame.transform.smoothscale(img, (CARD_W, CARD_H))
                CARD_IMAGES[f[:-4]] = img

    load_images()

    def card_to_filename(card_dict):
        """
        Convert card dict to image filename
        Your format: {"color": "Red", "value": "5"}
        Filename: r5 (without .png)
        """
        if not card_dict:
            return "back"

        color = card_dict.get("color", "").lower()
        value = card_dict.get("value", "")

        # Color codes
        color_map = {"red": "r", "green": "g", "blue": "b", "yellow": "y", "wild": "w"}
        c = color_map.get(color, "w")

        # Value codes
        if value.isdigit():
            return f"{c}{value}"
        elif "skip" in value.lower():
            return f"{c}s"
        elif "reverse" in value.lower():
            return f"{c}r"
        elif "draw 2" in value.lower():
            return f"{c}p2"
        elif "wild draw 4" in value.lower():
            return "wccp4"
        elif "wild" in value.lower():
            return "wcc"
        return "back"

    def img(card_dict, hidden=False):
        """Get card image"""
        if hidden or not card_dict:
            return CARD_IMAGES.get("back", CARD_IMAGES["back"])
        filename = card_to_filename(card_dict)
        return CARD_IMAGES.get(filename, CARD_IMAGES["back"])

    #positions of stuffs
    CX,CY=WIDTH//2,HEIGHT//2
    DRAW_POS=(CX + 20, CY - CARD_H//2)
    DISCARD_POS=(CX - CARD_W - 20, CY - CARD_H//2)
    PLAYER_Y=HEIGHT - CARD_H - 40

    #button arrangements
    font = pygame.font.SysFont("Arial", 30, True)

    EXIT_BTN=pygame.Rect(20, 20, 140, 65)
    KOT_BTN=pygame.Rect(WIDTH-170, 20, 150, 65)
    UNO_BTN=pygame.Rect(WIDTH-170, HEIGHT-90, 150, 65)

    #colour change mechs
    choosing_color = False
    selected_card_index = None
    COLOR_BTNS = {
        "Red": pygame.Rect(CX - 170, CY - 40, 80, 80),
        "Green": pygame.Rect(CX - 80, CY - 40, 80, 80),
        "Blue": pygame.Rect(CX + 10, CY - 40, 80, 80),
        "Yellow": pygame.Rect(CX + 100, CY - 40, 80, 80),
    }

    #drawing
    def button(rect, color, text, tc=(255,255,255)):
        pygame.draw.rect(win, color, rect, 0, 10)
        t = font.render(text, True, tc)
        win.blit(t, (rect.centerx - t.get_width()//2,
                     rect.centery - t.get_height()//2))

    def draw_color_popup():
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        win.blit(overlay, (0,0))

        box = pygame.Rect(CX-250, CY-120, 500, 220)
        pygame.draw.rect(win, (240,240,240), box, 0, 12)
        pygame.draw.rect(win, (0,0,0), box, 3, 12)

        title = font.render("Choose Color", True, (0,0,0))
        win.blit(title, (box.x+150, box.y+20))

        pygame.draw.rect(win, (200, 0, 0), COLOR_BTNS["Red"])
        pygame.draw.rect(win, (0, 180, 0), COLOR_BTNS["Green"])
        pygame.draw.rect(win, (0, 0, 200), COLOR_BTNS["Blue"])
        pygame.draw.rect(win, (230, 230, 0), COLOR_BTNS["Yellow"])

    #main loop
    running = True
    game_state = None

    while running:

        clock.tick(60)

        # Get game state from network listener
        if hasattr(network, 'game_state') and network.game_state:
            game_state = network.game_state.get("state")
            if player_id is None:
                player_id = network.game_state.get("your_player_id")

        if not game_state:
            # Show loading screen
            win.fill((20, 140, 60))
            loading = font.render("Waiting for game...", True, (255, 255, 255))
            win.blit(loading, (WIDTH // 2 - 150, HEIGHT // 2))
            pygame.display.update()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
            continue

        # Check for game over
        if game_state.get("game_over"):
            winner = game_state.get("winner")
            win.fill((0, 0, 0))
            game_over = font.render(f"{winner} WINS!", True, (255, 255, 0))
            win.blit(game_over, (WIDTH // 2 - 150, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(5000)
            running = False
            continue

        # Extract game data
        my_hand = game_state.get("your_hand", [])
        top_card = game_state.get("top_card")
        players = game_state.get("players", [])

        win.fill((20,140,60))

        # piles
        win.blit(img(None, hidden=True), DRAW_POS)  # Draw pile (hidden)
        if top_card:
            win.blit(img(top_card), DISCARD_POS)  # Top card

        # opponents
        ox = 60
        for i, p in enumerate(players):
            if i != player_id:
                # Draw card back
                win.blit(img(None, hidden=True), (ox, 60))
                # Show name and card count
                name_text = font.render(f"{p['name']}: {p['card_count']}", True, (255, 255, 255))
                win.blit(name_text, (ox, 30))
                # Show UNO indicator if they called it
                if p.get('called_uno') and p['card_count'] == 1:
                    uno_text = font.render("UNO!", True, (255, 255, 0))
                    win.blit(uno_text, (ox, 200))
                ox += 140

        # player hand
        rects = []
        start = CX - (len(my_hand) * (CARD_W + 15)) // 2
        for i, card_dict in enumerate(my_hand):
            r = pygame.Rect(start + i * (CARD_W + 15), PLAYER_Y, CARD_W, CARD_H)
            win.blit(img(card_dict), r)
            rects.append((i, card_dict, r))  # Store index, card, and rect

        # buttons
        button(EXIT_BTN, (180,40,40), "EXIT")
        # button(KOT_BTN, (40,80,200), "KOT")     no need for now
        button(UNO_BTN, (230,210,40), "UNO", (0,0,0))

        if choosing_color:
            draw_color_popup()

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                if choosing_color:
                    for color_name, r in COLOR_BTNS.items():
                        if r.collidepoint(mx, my):
                            # Send play card with chosen color
                            network.send_action("play_card",
                                                card_index=selected_card_index,
                                                chosen_color=color_name)
                            choosing_color = False
                            selected_card_index = None
                    continue

                for i, card_dict, r in rects:
                    if r.collidepoint(mx, my):
                        # Check if it's a Wild card
                        if card_dict.get("color") == "Wild":
                            # Need to choose color first
                            selected_card_index = i
                            choosing_color = True
                        else:
                            # Play card immediately
                            network.send_action("play_card", card_index=i)
                        break

                if pygame.Rect(*DRAW_POS, CARD_W, CARD_H).collidepoint(mx, my):
                    network.send_action("draw_card")

                if UNO_BTN.collidepoint(mx, my):
                    print("[GUI] UNO called! (not implemented yet)")
                    network.send_action("call_uno")
                    print("[GUI] Called UNO!")

                # KOT button removed

                if EXIT_BTN.collidepoint(mx, my):
                    running = False

pygame.quit()
