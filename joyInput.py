import pygame

pygame.init()

# create a window to display input values
WINDOW_SIZE = (800, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Joystick Test")

# find all connected joystick devices
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
print(f"Found {joystick_count} joystick devices")

# if there are any joystick devices connected
if joystick_count > 0:
    # allow user to select a joystick device
    print("Select a joystick device:")
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        print(f"{i}: {joystick.get_name()}")

    joystick_index = int(input("Enter joystick index: "))
    joystick = pygame.joystick.Joystick(joystick_index)
    joystick.init()
    print(f"Using joystick '{joystick.get_name()}'")

    # display input values in real-time
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (0, 0, 0), (50, 50, 700, 500), 1)

        # Add a Title
        text_surface = pygame.font.SysFont(None, 24).render(f"{joystick.get_name()}", True, (0, 0, 0))
        screen.blit(text_surface, (10, 10))

        # iterate over all joystick axes and display their value
        for i in range(joystick.get_numaxes()):
            axis_value = joystick.get_axis(i)
            text_surface = pygame.font.SysFont(None, 24).render(f"Axis {i}: {axis_value:.2f}", True, (0, 0, 0))
            screen.blit(text_surface, (60 + (i%5)*140, 60 + (i//5)*40))

        # iterate over all joystick buttons and display their value
        for i in range(joystick.get_numbuttons()):
            button_value = joystick.get_button(i)
            text_surface = pygame.font.SysFont(None, 24).render(f"Button {i}: {button_value}", True, (0, 0, 0))
            screen.blit(text_surface, (60 + (i%5)*140, 220 + (i//5)*40))

        # iterate over DPad axes and display their value
        for i in range(joystick.get_numhats()):
            hat_value = joystick.get_hat(i)
            text_surface = pygame.font.SysFont(None, 24).render(f"DPad {i}: {hat_value}", True, (0, 0, 0))
            screen.blit(text_surface, (60 + (i%5)*140, 380 + (i//5)*40))

        pygame.display.update()

    pygame.quit()