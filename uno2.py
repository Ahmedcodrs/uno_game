import pygame
import sys

def startlobby(username):
    pygame.init()

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
    players=[{"name":username,"ready":False,}]
    maxplayers=4

    #ready button
    readyrect=pygame.Rect((width-400)//2,height-150,400,80)
    pygame.key.set_repeat(350,40)


    #aloo ke parathe are tasty nom nom nom and draw
    def redraw():
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
                namesurf = namefont.render(p["name"], True, (255, 255, 255))
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
        playerready = players[0]["ready"]
        if playerready == True:
            btncolor = (120, 120, 120)
            label = "Press ENTER to Unready"
        else:
            btncolor = (0, 200, 0)
            label = "Press ENTER to Ready"

        pygame.draw.rect(win, btncolor, readyrect, border_radius=10)
        labelsurf = namefont.render(label, True, (255, 255, 255))
        win.blit(labelsurf,(readyrect.centerx - labelsurf.get_width() // 2,readyrect.centery - labelsurf.get_height() // 2))

        pygame.display.flip()

                

        
    

    
    # Main loop
    running = True
    while running:
        clock.tick(60)

        #Event handling
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False


            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    running=False


                elif event.key==pygame.K_RETURN:
                    players[0]["ready"] = not players[0]["ready"]

        redraw()

    pygame.quit()














                          
