import pygame
import socket
import time
import pickle
def startlobby(username,network):

    #window
    width,height=1280,720
    win=pygame.display.set_mode((width,height))
    pygame.display.set_caption("UNO-Matchmaking Lobby")
    clock=pygame.time.Clock()

    #font
    titlefont = pygame.font.SysFont("Arial", 60, bold=True)
    namefont  = pygame.font.SysFont("Arial", 40, bold=True)
    smallfont = pygame.font.SysFont("Arial", 30)

    #title
    titletext=titlefont.render("UNO-Matchmaking Lobby",True,(255,255,255))
    titlerect=titletext.get_rect(center=(width//2,50))
    
    #player list area
    xbox=width//2-300
    ybox=150
    wbox=600
    hbox=320
    hslot=hbox//4

    #player data
    players=[]
    maxplayers=4

    #ready button
    readyrect=pygame.Rect((width-400)//2,height-150,400,80)
    pygame.key.set_repeat(350,40)
    last_update = 0




    #aloo ke parathe are tasty nom nom nom and draw
    def redraw(players, your_index):
        win.fill((0,100,0))
        win.blit(titletext,titlerect)

        #to draw player list 
        pygame.draw.rect(win, (40, 40, 40), (xbox,ybox,wbox,hbox))
        pygame.draw.rect(win, (200, 200, 200),(xbox,ybox,wbox,hbox), 3)

        # Draw each slot (empty or filled)
        for i in range(maxplayers):
            slottop = ybox + i * hslot

            # horizontal divider
            pygame.draw.line(win, (120, 120, 120),(xbox, slottop + hslot),(xbox + wbox, slottop + hslot),2)

            if i < len(players):
                p = players[i]

                # player name
                namesurf = namefont.render(p["username"], True, (255, 255, 255))
                win.blit(namesurf, (xbox + 12, slottop + (hslot - namesurf.get_height()) // 2))

                # ready status
                if p["ready"] == True:
                    status = "Ready"
                    statuscolor = (0, 200, 0)
                else:
                    status = "Not Ready"
                    statuscolor = (200, 50, 50)

                statussurf = namefont.render(status, True, statuscolor)
                win.blit(statussurf,(xbox + wbox - 12 - statussurf.get_width(),slottop + (hslot - statussurf.get_height()) // 2))
            else:
                # empty waiting slot
                empt = namefont.render("Waiting...", True, (180, 180, 180))
                win.blit(empt, (xbox + 12, slottop + (hslot - empt.get_height()) // 2))

        # ready counter
        readycount = 0
        for p in players:
            if p["ready"] == True:
                readycount = readycount + 1
            else:
                readycount = readycount

        totalplayers = len(players)
        countersurf = smallfont.render(f"Players Ready: {readycount}/{totalplayers}", True, (255, 255, 0))
        win.blit(countersurf, (width // 2 - countersurf.get_width() // 2, ybox + hbox + 12))




        # ready button display
        #and checks your_index which is like a roll number for using within this function
        if your_index is not None:
            playerready = players[your_index]["ready"]
            if playerready == True:
                btncolor = (120, 120, 120)
                label = "Press ENTER to Unready"
            else:
                btncolor = (0, 200, 0)
                label = "Press ENTER to Ready"
        else:
            # You're not in the list yet
            btncolor = (100, 100, 100)
            label = "Connecting..."

        pygame.draw.rect(win, btncolor, readyrect, border_radius=10)
        labelsurf = namefont.render(label, True, (255, 255, 255))
        win.blit(labelsurf,(readyrect.centerx - labelsurf.get_width() // 2,readyrect.centery - labelsurf.get_height() // 2))

        pygame.display.flip()

                




    
    # Main loop
    running = True

    while running:
        clock.tick(60)
        #read from shared state
        players = network.players.copy()

        #check for game started
        if network.game_started:
            print("Game starting")
            running = False
            break

        #find index
        your_index = None
        for i, p in enumerate(players):
            if p.get("username") == username:
                your_index = i
                break

        #Event handling
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False


            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    running=False


                elif event.key==pygame.K_RETURN:
                    if your_index is not None:
                        #send action enough
                        network.send_action("toggle_ready")
                        print("sent toggle_ready")



        redraw(players,your_index)

    pygame.quit()

















                          
