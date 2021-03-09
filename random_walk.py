"""
author: Bartosz Ambroży Greń
mail: bartosz.gren [at] student.uw.edu.pl

To jest program generujący spacer losowe (random walk). Moim celem
nie było napisanie afektywnego kodu przedstawiającego błądzenie losowe,
a zaprezentowanie: 
* jak zwizualizować trajektorię
* jak wygenerować klatki do animacji
* jak wygenerować animację bezpośrednio korzystając
  z matplotlib.animation

Przyjrzyjcie się programowi, zrozumcie go (w razie czego pytajcie)
i śmiało możecie rozwiązania z tego implementować u siebie.
"""
import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import trange, tqdm
# tqdm -- fajna biblioteka do wizualizacji postępu pętli
# os -- biblioteka z funkcjami systemowym


class Simul(object):
    def __init__(self, no_of_walkers=10, no_of_steps=400, steps_per_frame = 4,
                 export_frames = True, export_trajectory = True, 
                 export_dist = True):
        ## zmienne, które się nie zmieniają w trakcie programu
        self.walkers = [Walker() for n in range(no_of_walkers)]
        self.max_step = no_of_steps
        self.steps_per_frame = steps_per_frame
        # export parameters
        self.trajectory = export_trajectory
        self.frames = export_frames
        self.dist = export_dist

        ## zmienne, których wartości będą aktualizowane
        self.step = 0
        # inicjalizuję tablicę, w której będę przechowywać wszystkie
        # współrzędne
        self.x = np.zeros([self.max_step+1, len(self.walkers)], dtype=np.int16)
        self.y = np.zeros([self.max_step+1, len(self.walkers)], dtype=np.int16)
        # z góry wiem jaki będzie jej finalny rozmiar więc mogę sobie
        # pozwolić na stworzenie jej z dokładnie takimi wymiarami
        # jakie chcę: liczba_wszystkich_kroków * liczba_błądzeń;

        # mogę też zdefiniować typ zmiennej (dtype) w tablicy, domyślnie
        # to jest (chyba, może zależy od systemu?) np.int64, czyli
        # 8 bajtów na liczbę (wartości od 9223372036854775808 do 
        # 9223372036854775807), tyle nie jest potrzebne, wystarczy
        # np.int16 czyli 2 bajty na liczbę (wartości od -32768 do 32767)
        # co tutaj w pełni wystarczy, a tablica zajmie 4x mniej miejsca.

        # jeśli będzie drukowana trajektoria na koniec, to zainicjuj
        if self.frames:
            self.initiate_frame_print()
        # główny program
        self.main()
        if self.trajectory:
            self.save_frame('trajectory.png') 
        if self.dist:
            self.calc_dist()

    def calc_dist(self):
        steps, walkers = np.shape(self.x)
        time = np.arange(steps)
        dist_theory = np.sqrt(time)
        # metryka kartezjańska
        dist      = np.sqrt(np.square(self.x) + np.square(self.y))
        dist_mean = np.mean(dist, axis = 1)
        plt.tick_params(axis = 'both', which = 'both', direction='in',
                        right=True, top=True)
        plt.xlim(0,steps)
        plt.xlabel('No of steps')
        plt.ylabel('Distance')
        for walker,i in zip(self.walkers, range(len(self.walkers))):
            plt.plot(time, dist, linestyle='dashed', linewidth=1)
        plt.plot(time, dist_mean, linestyle='dashed', color='black', 
                 linewidth=2, label='RW mean')
        plt.plot(time, dist_theory, color='black', linewidth=3, 
                 label='RW theory')
        plt.legend()
        plt.title('Random walk')
        plt.savefig('distance.png', dpi=300)
        # zamykamy na koniec, by nie zawalać pamięci
        plt.close()   


    def main(self):
        # główna pętla po czasie, trange z biblioteki tqdm
        for t in trange(self.max_step+1):
            self.step += 1
            # pętla po spacerowiczach i ich indeksie
            for walker, i in zip(self.walkers, range(len(self.walkers))):
                walker.make_step()
                # aktualizuję tablicę przechowującą współrzędne
                self.x[t,i] = walker.x
                self.y[t,i] = walker.y
            # zapisuję klatkę symulacji co „steps_per_frame" kroków
            # dlaczego nie zapisywać wszystkich? obliczenia są super
            # szybkie względem szybkości produkowania obrazków
            # i rysowanie po każdym kroku bardzo spowalnia działanie 
            # programu
            if self.frames and t%self.steps_per_frame == 0:
                self.save_frame('frames/f_{:05d}.png'.format(self.frame))
                self.frame += 1


    def initiate_frame_print(self):
        self.frame = 0
        # tworzy folder na klatki symulacyjne
        try:
            os.mkdir('frames')
        except:
            pass


    def save_frame(self, name):
        # parametry dodające osie na górze i po prawej, nie tylko na 
        # dole i po lewej
        plt.tick_params(axis = 'both', which = 'both', direction='in',
                        right=True, top=True)
        # równy rozmiar osi
        plt.gca().set_aspect('equal', adjustable='box')
        # średni dystans pokonany przez spacer losowy jest
        # proporcjonalny do pierwiastka liczby kroków
        box_sidelength = int(np.sqrt(self.max_step))*5
        plt.xlim(-box_sidelength/2, box_sidelength/2)
        plt.ylim(-box_sidelength/2, box_sidelength/2)
        for walker,i in zip(self.walkers, range(len(self.walkers))):
            plt.scatter(walker.x, walker.y)
            plt.plot(self.x[:self.step,i], self.y[:self.step,i], linewidth=1)
        # bbox_inches='tight', pand_inches=0 -- zostawiają minimalną
        # ilość przestrzeni poza samym wykresem na generowanym obrazku
        # dpi -- jakość obrazka
        plt.savefig(name, bbox_inches='tight', pad_inches=0., dpi=300)
        # zamykamy na koniec, by nie zawalać pamięci
        plt.close()   
        

# klasa spacerowicza 
class Walker(object):
    def __init__(self):
        # współrzędne zapisałem jako pojedyncze liczby, może być też
        # lista rzecz jasna
        self.x = 0
        self.y = 0

    def make_step(self):
        # lista możliwych kroków
        possible_moves = [self.go_up, self.go_left, self.go_down, 
                          self.go_right]
        # losuję jedną z możliwych funkcji i wykonuję ruch
        np.random.choice(possible_moves)()
        
    def go_up(self):
        self.y += 1

    def go_down(self):
        self.y -= 1

    def go_right(self):
        self.x += 1

    def go_left(self):
        self.x -= 1

if __name__ == '__main__':
    Simul()
