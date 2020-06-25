#built-in
import random

#HBC (Home Brew Class)
import lottery


class SelectEmployerionStrategy:
    def select(self, employee, employers, num = 1):
        pass


class RandomSelectEmployerStrategy(SelectEmployerionStrategy):
    def select(self, employee, employers, num = 1):
        return random.sample(employers, num)


# If you need other selection method, then create a new class which is inherited with SelectionStorategy class.
# The SelectionStorategy class just force to have select method and the arguments of the method.
class RouletteSelectEmployerStrategy(SelectEmployerionStrategy):
    default_probability = 0.1 #いいのかな?

    # The agent selects the employer of the num in the list of employers.
    def select(self, employee, employers, num = 1):
        # We select the employers baced on reward from the employers
        # 今後はクビを切られたから確率を下げるとか入れてもいいかも
        roulette_src = {}
        default_prob = 0.1
        if sum(employee.rewards.values()) != 0 :
            default_prob = RouletteSelectEmployerStrategy.default_probability * min(employee.rewards.values())
        for employer in employers:
            if employer in employee.rewards.keys():
                roulette_src[employer] = employee.rewards[employer]
            else:
                roulette_src[employer] = default_prob
        roulette = lottery.Roulette(roulette_src)


        #Check the number of selections whether is over the size of employers list or not.
        if len(employers) <= num:
            return employers

        # collect employer objects whose selected id 
        selected_employers = []
        for i in range(num):
            employer = roulette.dice()
            selected_employers.append(employer)
            roulette.delete(employer)
        
        return selected_employers
        pass
