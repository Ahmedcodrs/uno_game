import pygame
pygame.init()

#this is the window specs,captions and clock

width = 1280
height = 720
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("UNO")  
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 60, bold=True)
texttodisplay = "UNO"



#for the title
def title():
    global textsurface
    global textrect
    textcolor = (255, 255, 255)  
    textsurface = font.render(texttodisplay, True, textcolor)
    textrect = textsurface.get_rect()
    textrect.centerx = width // 2
    textrect.top = 10

#keeps drawing the bg and title 
def redrawgamewin(username):
    win.fill((0, 100, 0))
    pygame.draw.rect(win, (128, 128, 128), textboxrect, 6)
    win.blit(textsurface, textrect)

    # FOR THE USERNAME ENTER TITLE
    win.blit(promptsurf, promptrect)
    pygame.draw.rect(win, (40, 40, 40), inputrect)
    pygame.draw.rect(win, (200, 200, 200), inputrect, 3)
    textsurf = inputfont.render(username, True, (255, 255, 255))
    win.blit(textsurf, (inputrect.x + 12, inputrect.y + (inputrect.height - textsurf.get_height()) // 2))

    pygame.display.flip()




    
#title box and function call
title()
boxpadding = 10
textboxrect = pygame.Rect(textrect.left - boxpadding,textrect.top - boxpadding,textrect.width + (2 * boxpadding),textrect.height + (2 * boxpadding))


#username entering parameters 
inputfont = pygame.font.SysFont('Arial', 38)
username = ""
maxlen = 16
inputw, inputh = 700, 80
inputrect = pygame.Rect((width - inputw)//2, (height - inputh)//2 + 40, inputw, inputh)
promptsurf = inputfont.render("Enter your username (press Enter):", True, (255, 255, 255))
promptrect = promptsurf.get_rect(center=(width // 2, inputrect.top - 40))

#hold key/backspace 
pygame.key.set_repeat(350, 40)


# main loop
def username_screen():
    running = True
    username = ''
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            #this is the keyboard press event where it registers the key and fucntions acc to that
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    if username.strip():
                        print("Username:", username.strip())  # replace with lobby transition, not done till now will add with mysql connectivity
                        return username


                elif event.key == pygame.K_BACKSPACE:
                    if username:
                        username = username[:-1]
                else:
                    ch = event.unicode
                    if ch and len(username) < maxlen and (ch.isalnum() or ch in "_-"):
                        username += ch

        redrawgamewin(username)

    pygame.quit()

